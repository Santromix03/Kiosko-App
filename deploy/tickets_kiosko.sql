-- =====================================================================
-- Tickets del kiosco: listar los pedidos del día y cancelarlos
-- Ejecutar UNA vez en Supabase -> SQL Editor (es seguro repetirlo).
--
-- Crea dos funciones:
--   public.get_today_tickets()
--       Devuelve los pedidos de HOY (hora de Colombia) con sus productos y
--       adiciones, en el mismo formato que usa el panel. Así el kiosco no
--       necesita permisos para leer las tablas de ventas.
--   public.cancel_ticket(p_order_id bigint)
--       Cancela un pedido de HOY: devuelve el stock de las adiciones y de
--       los productos con stock directo, y borra el ticket. Todo en una
--       sola transacción (si algo falla, no se borra nada).
--
-- Las dos solo las pueden usar administradores o empleados activos (los
-- mismos que entran al kiosco con su cuenta). La clave anónima no puede.
-- =====================================================================

-- ---------- 1) Pedidos de hoy ----------
create or replace function public.get_today_tickets()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_day date := (now() at time zone 'America/Bogota')::date;
  v_tickets jsonb;
begin
  if coalesce(public.my_role(), 'ninguno') not in ('admin', 'employee') then
    raise exception 'Solo un empleado activo puede ver los tickets';
  end if;

  select coalesce(jsonb_agg(ticket order by num), '[]'::jsonb)
    into v_tickets
    from (
      select o.ticket_number as num,
             jsonb_build_object(
               'id', o.id,
               'ticket_number', o.ticket_number,
               'created_at', o.created_at,
               'total', o.total,
               'items', coalesce((
                 select jsonb_agg(
                          jsonb_build_object(
                            'name', oi.name,
                            'quantity', oi.quantity,
                            'unit_price', oi.unit_price,
                            'addons', coalesce((
                              select jsonb_agg(
                                       jsonb_build_object(
                                         'name', a.name,
                                         'unit_price', a.unit_price
                                       ) order by a.name)
                                from public.order_item_addons a
                               where a.order_item_id = oi.id
                            ), '[]'::jsonb)
                          ) order by oi.id)
                   from public.order_items oi
                  where oi.order_id = o.id
               ), '[]'::jsonb)
             ) as ticket
        from public.orders o
       where o.order_date = v_day
    ) s;

  return v_tickets;
end;
$$;

-- ---------- 2) Cancelar un pedido de hoy ----------
create or replace function public.cancel_ticket(p_order_id bigint)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_order public.orders;
  v_line  record;
begin
  -- Solo personal con acceso (admin o empleado activo)
  if coalesce(public.my_role(), 'ninguno') not in ('admin', 'employee') then
    raise exception 'Solo un empleado activo puede cancelar tickets';
  end if;

  -- Bloquea el pedido para que dos personas no lo cancelen a la vez
  select * into v_order
    from public.orders
   where id = p_order_id
     for update;

  if not found then
    raise exception 'Ese ticket ya no existe (puede que ya lo hayan cancelado)';
  end if;

  -- Solo tickets del día, en hora de Colombia
  if v_order.order_date <> (now() at time zone 'America/Bogota')::date then
    raise exception 'Solo se pueden cancelar tickets de hoy';
  end if;

  -- Devolver stock de las adiciones (cantidad total pedida por adición)
  for v_line in
    select a.addon_id, sum(oi.quantity)::int as qty
      from public.order_item_addons a
      join public.order_items oi on oi.id = a.order_item_id
     where oi.order_id = p_order_id
       and a.addon_id is not null
     group by a.addon_id
  loop
    update public.addons
       set stock = stock + v_line.qty
     where id = v_line.addon_id;
  end loop;

  -- Devolver stock de productos con control directo (los de receta no)
  for v_line in
    select oi.product_id, sum(oi.quantity)::int as qty
      from public.order_items oi
     where oi.order_id = p_order_id
       and oi.product_id is not null
     group by oi.product_id
  loop
    update public.products
       set stock = stock + v_line.qty
     where id = v_line.product_id
       and stock_mode = 'direct';
  end loop;

  -- Borrar el pedido (primero los hijos)
  delete from public.order_item_addons
   where order_item_id in (
     select id from public.order_items where order_id = p_order_id
   );
  delete from public.order_items where order_id = p_order_id;
  delete from public.orders where id = p_order_id;

  return jsonb_build_object(
    'ticket_number', v_order.ticket_number,
    'total', v_order.total
  );
end;
$$;

-- ---------- Permisos ----------
-- Solo usuarios con sesión iniciada (el kiosco entra con la cuenta del
-- empleado). La clave pública anónima NO puede ver ni cancelar ventas.
revoke all on function public.get_today_tickets() from public, anon;
grant execute on function public.get_today_tickets() to authenticated;

revoke all on function public.cancel_ticket(bigint) from public, anon;
grant execute on function public.cancel_ticket(bigint) to authenticated;

-- Comprobación rápida (opcional):
--   select public.my_role();
--   select public.get_today_tickets();
