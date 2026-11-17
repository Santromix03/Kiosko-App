-- ============================================================
-- CARTA GOD'S WISHES — semilla del menu para el kiosko
-- Generada automaticamente a partir de las fotos de la carta.
--
-- Que hace:
--   1. Borra la categoria de prueba (id 11).
--   2. Crea las 20 categorias de la carta (ids 101-120).
--   3. Crea los productos (stock_mode='none', stock=0 -> sin
--      ingredientes, siempre disponibles, sin control de stock).
--   4. Crea los 11 ADICIONALES de la carta (stock 9999) y los
--      enlaza a todas las categorias de comida.
--
-- Como usarlo: Supabase -> SQL Editor -> pegar todo -> Run.
-- Se puede volver a ejecutar: no duplica nada.
-- Las imagenes se suben aparte a Storage -> bucket 'product-images'
-- carpeta 'menu/' (ver deploy/imagenes_de_la_carta.md).
-- ============================================================

-- 1) categoria de prueba del panel
delete from categories where id = 11;

-- 2) categorias de la carta
insert into categories (id, name, sort_order, active) values
  (101, 'Pizzas', 1, true),
  (102, 'Arepas rellenas', 2, true),
  (103, 'Salchipapa', 3, true),
  (104, 'Patacones rellenos', 4, true),
  (105, 'Hamburguesas', 5, true),
  (106, 'Perros calientes', 6, true),
  (107, 'Sandwich', 7, true),
  (108, 'Picadas papas', 8, true),
  (109, 'Picadas patacón', 9, true),
  (110, 'Salvajadas', 10, true),
  (111, 'Desgranado', 11, true),
  (112, 'Asados', 12, true),
  (113, 'Cervezas', 13, true),
  (114, 'Micheladas cerveza', 14, true),
  (115, 'Micheladas soda', 15, true),
  (116, 'Jugos granizados', 16, true),
  (117, 'Limonadas', 17, true),
  (118, 'Mocktails', 18, true),
  (119, 'Cocteles', 19, true),
  (120, 'Bebidas', 20, true)
on conflict (id) do update
set name = excluded.name, sort_order = excluded.sort_order, active = true;

-- 3) productos de la carta (sin ingredientes: stock_mode 'none')

-- Pizzas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (101, 'Jamón y queso personal', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 1, 'none', 0),
  (101, 'Jamón y queso familiar', 30000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 2, 'none', 0),
  (101, 'Chori ternera personal', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 3, 'none', 0),
  (101, 'Chori ternera familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 4, 'none', 0),
  (101, 'Butifarra personal', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 5, 'none', 0),
  (101, 'Butifarra familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 6, 'none', 0),
  (101, 'Hawaiana personal', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 7, 'none', 0),
  (101, 'Hawaiana familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 8, 'none', 0),
  (101, 'Jamón pollo personal', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 9, 'none', 0),
  (101, 'Jamón pollo familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 10, 'none', 0),
  (101, 'Chori casero personal', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 11, 'none', 0),
  (101, 'Chori casero familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 12, 'none', 0),
  (101, 'Chori buti personal', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 13, 'none', 0),
  (101, 'Chori buti familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 14, 'none', 0),
  (101, 'Chori maíz personal', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 15, 'none', 0),
  (101, 'Chori maíz familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 16, 'none', 0),
  (101, 'Pollo maíz personal', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 17, 'none', 0),
  (101, 'Pollo maíz familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 18, 'none', 0),
  (101, 'Cerdo maíz personal', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 19, 'none', 0),
  (101, 'Cerdo maíz familiar', 34000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 20, 'none', 0),
  (101, 'Ranchera pollo personal', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 21, 'none', 0),
  (101, 'Ranchera pollo familiar', 36000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 22, 'none', 0),
  (101, 'Salchicha personal', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 23, 'none', 0),
  (101, 'Salchicha familiar', 36000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 24, 'none', 0),
  (101, 'Suiza personal', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 25, 'none', 0),
  (101, 'Suiza familiar', 36000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 26, 'none', 0),
  (101, 'Ranchera personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 27, 'none', 0),
  (101, 'Ranchera familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 28, 'none', 0),
  (101, 'Buti ranchera personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 29, 'none', 0),
  (101, 'Buti ranchera familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 30, 'none', 0),
  (101, 'La deliciosa personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 31, 'none', 0),
  (101, 'La deliciosa familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 32, 'none', 0),
  (101, 'La bomba personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 33, 'none', 0),
  (101, 'La bomba familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 34, 'none', 0),
  (101, 'Mexicana personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 35, 'none', 0),
  (101, 'Mexicana familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 36, 'none', 0),
  (101, '3 carnes personal', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 37, 'none', 0),
  (101, '3 carnes familiar', 37000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 38, 'none', 0),
  (101, '4 carnes personal', 16000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 39, 'none', 0),
  (101, '4 carnes familiar', 38000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 40, 'none', 0),
  (101, 'De la casa personal', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 41, 'none', 0),
  (101, 'De la casa familiar', 40000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/pizza.jpg', true, 42, 'none', 0);

-- Arepas rellenas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (102, 'Jamón y queso', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 1, 'none', 0),
  (102, 'Ternera', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 2, 'none', 0),
  (102, 'Butifarra', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 3, 'none', 0),
  (102, 'Chori casero', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 4, 'none', 0),
  (102, 'Chori buti', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 5, 'none', 0),
  (102, 'Pollo', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 6, 'none', 0),
  (102, 'Cerdo', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 7, 'none', 0),
  (102, 'Mixta', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 8, 'none', 0),
  (102, 'Suiza', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 9, 'none', 0),
  (102, 'Ranchera', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 10, 'none', 0),
  (102, 'Chori pollo', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 11, 'none', 0),
  (102, 'Chori cerdo', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 12, 'none', 0),
  (102, 'Chori suiza', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 13, 'none', 0),
  (102, 'De la casa', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/arepa-rellena.jpg', true, 14, 'none', 0);

-- Salchipapa
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (103, 'Sencilla media', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-media.jpg', true, 1, 'none', 0),
  (103, 'Sencilla entera', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 2, 'none', 0),
  (103, 'Salchi pollo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-media.jpg', true, 3, 'none', 0),
  (103, 'Salchi pollo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 4, 'none', 0),
  (103, 'Salchi cerdo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-media.jpg', true, 5, 'none', 0),
  (103, 'Salchi cerdo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 6, 'none', 0),
  (103, 'Salchi suiza media', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-media.jpg', true, 7, 'none', 0),
  (103, 'Salchi suiza entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 8, 'none', 0),
  (103, 'Salchi de la casa media', 16000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-media.jpg', true, 9, 'none', 0),
  (103, 'Salchi de la casa entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 10, 'none', 0),
  (103, 'Super clásica entera', 22000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 11, 'none', 0),
  (103, 'Extra clásica entera', 32000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 12, 'none', 0),
  (103, 'Grande plus entera', 50000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salchipapa-entera.jpg', true, 13, 'none', 0);

-- Patacones rellenos
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (104, 'Sencillo', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 1, 'none', 0),
  (104, 'Ternera', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 2, 'none', 0),
  (104, 'Butifarra', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 3, 'none', 0),
  (104, 'Chori casero', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 4, 'none', 0),
  (104, 'Chori buti', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 5, 'none', 0),
  (104, 'Pollo', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 6, 'none', 0),
  (104, 'Cerdo', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 7, 'none', 0),
  (104, 'Mixto', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 8, 'none', 0),
  (104, 'De la casa', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/patacon-relleno.jpg', true, 9, 'none', 0);

-- Hamburguesas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (105, 'Sencilla', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 1, 'none', 0),
  (105, 'Ternera', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 2, 'none', 0),
  (105, 'Chori casero', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 3, 'none', 0),
  (105, 'Cerdo', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 4, 'none', 0),
  (105, 'Pollo', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 5, 'none', 0),
  (105, 'Suiza', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 6, 'none', 0),
  (105, 'Ranchera', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 7, 'none', 0),
  (105, 'Mixta', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 8, 'none', 0),
  (105, 'Doble carne', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 9, 'none', 0),
  (105, 'Triple carne', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 10, 'none', 0),
  (105, 'De la casa', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/hamburguesa.jpg', true, 11, 'none', 0);

-- Perros calientes
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (106, 'Sencillo', 5000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 1, 'none', 0),
  (106, 'Doble queso', 7000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 2, 'none', 0),
  (106, 'Jamón y queso', 7000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 3, 'none', 0),
  (106, 'Doble salchicha', 7000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 4, 'none', 0),
  (106, 'Mini suizo', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 5, 'none', 0),
  (106, 'Ternera', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 6, 'none', 0),
  (106, 'Butifarra', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 7, 'none', 0),
  (106, 'Chori casero', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 8, 'none', 0),
  (106, 'Pollo', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 9, 'none', 0),
  (106, 'Cerdo', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 10, 'none', 0),
  (106, 'Suizo', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 11, 'none', 0),
  (106, 'Ranchera', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 12, 'none', 0),
  (106, 'Mixta', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 13, 'none', 0),
  (106, 'Chori pollo', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 14, 'none', 0),
  (106, 'Chori cerdo', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 15, 'none', 0),
  (106, 'De la casa', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/perro-caliente.jpg', true, 16, 'none', 0);

-- Sandwich
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (107, 'Jamón y queso', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 1, 'none', 0),
  (107, 'Butifarra', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 2, 'none', 0),
  (107, 'Ternera', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 3, 'none', 0),
  (107, 'Chori casero', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 4, 'none', 0),
  (107, 'Cerdo', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 5, 'none', 0),
  (107, 'Pollo', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 6, 'none', 0),
  (107, 'Mixto', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 7, 'none', 0),
  (107, 'Suiza', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 8, 'none', 0),
  (107, 'Ranchero', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 9, 'none', 0),
  (107, 'Chori pollo', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 10, 'none', 0),
  (107, 'Chori cerdo', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 11, 'none', 0),
  (107, 'Chori suizo', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 12, 'none', 0),
  (107, 'De la casa', 16000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/sandwich.jpg', true, 13, 'none', 0);

-- Picadas papas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (108, 'Ternera media', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 1, 'none', 0),
  (108, 'Ternera entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 2, 'none', 0),
  (108, 'Butifarra media', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 3, 'none', 0),
  (108, 'Butifarra entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 4, 'none', 0),
  (108, 'Chori casero media', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 5, 'none', 0),
  (108, 'Chori casero entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 6, 'none', 0),
  (108, 'Chori buti media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 7, 'none', 0),
  (108, 'Chori buti entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 8, 'none', 0),
  (108, 'Pollo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 9, 'none', 0),
  (108, 'Pollo entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 10, 'none', 0),
  (108, 'Cerdo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 11, 'none', 0),
  (108, 'Cerdo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 12, 'none', 0),
  (108, 'Suizo media', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 13, 'none', 0),
  (108, 'Suizo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 14, 'none', 0),
  (108, 'Mixta media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 15, 'none', 0),
  (108, 'Mixta entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 16, 'none', 0),
  (108, 'Ranchera media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 17, 'none', 0),
  (108, 'Ranchera entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 18, 'none', 0),
  (108, 'Chori pollo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 19, 'none', 0),
  (108, 'Chori pollo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 20, 'none', 0),
  (108, 'Chori cerdo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 21, 'none', 0),
  (108, 'Chori cerdo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 22, 'none', 0),
  (108, 'Chori suizo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 23, 'none', 0),
  (108, 'Chori suizo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 24, 'none', 0),
  (108, 'De la casa media', 16000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-media.jpg', true, 25, 'none', 0),
  (108, 'De la casa entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-papas-entera.jpg', true, 26, 'none', 0);

-- Picadas patacón
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (109, 'Ternera media', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 1, 'none', 0),
  (109, 'Ternera entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 2, 'none', 0),
  (109, 'Butifarra media', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 3, 'none', 0),
  (109, 'Butifarra entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 4, 'none', 0),
  (109, 'Chori casero media', 11000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 5, 'none', 0),
  (109, 'Chori casero entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 6, 'none', 0),
  (109, 'Chori buti media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 7, 'none', 0),
  (109, 'Chori buti entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 8, 'none', 0),
  (109, 'Pollo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 9, 'none', 0),
  (109, 'Pollo entera', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 10, 'none', 0),
  (109, 'Cerdo media', 13000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 11, 'none', 0),
  (109, 'Cerdo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 12, 'none', 0),
  (109, 'Suizo media', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 13, 'none', 0),
  (109, 'Suizo entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 14, 'none', 0),
  (109, 'Mixta media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 15, 'none', 0),
  (109, 'Mixta entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 16, 'none', 0),
  (109, 'Ranchera media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 17, 'none', 0),
  (109, 'Ranchera entera', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 18, 'none', 0),
  (109, 'Chori pollo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 19, 'none', 0),
  (109, 'Chori pollo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 20, 'none', 0),
  (109, 'Chori cerdo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 21, 'none', 0),
  (109, 'Chori cerdo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 22, 'none', 0),
  (109, 'Chori suizo media', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 23, 'none', 0),
  (109, 'Chori suizo entera', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 24, 'none', 0),
  (109, 'De la casa media', 16000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-media.jpg', true, 25, 'none', 0),
  (109, 'De la casa entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/picada-patacon-entera.jpg', true, 26, 'none', 0);

-- Salvajadas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (110, 'Cupido', 35000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 1, 'none', 0),
  (110, 'La Diosa', 50000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 2, 'none', 0),
  (110, 'La Deliciosa', 65000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 3, 'none', 0),
  (110, 'El gran Zeus', 80000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 4, 'none', 0),
  (110, 'De la casa', 100000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 5, 'none', 0),
  (110, 'La grupal', 150000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/salvajadas-grandes.jpg', true, 6, 'none', 0);

-- Desgranado
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (111, 'Ternera media', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 1, 'none', 0),
  (111, 'Ternera entera', 22000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 2, 'none', 0),
  (111, 'Butifarra media', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 3, 'none', 0),
  (111, 'Butifarra entera', 22000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 4, 'none', 0),
  (111, 'Chori casero media', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 5, 'none', 0),
  (111, 'Chori casero entera', 22000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 6, 'none', 0),
  (111, 'Chori buti media', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 7, 'none', 0),
  (111, 'Chori buti entera', 22000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 8, 'none', 0),
  (111, 'Pollo media', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 9, 'none', 0),
  (111, 'Pollo entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 10, 'none', 0),
  (111, 'Cerdo media', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 11, 'none', 0),
  (111, 'Cerdo entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 12, 'none', 0),
  (111, 'Suiza media', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 13, 'none', 0),
  (111, 'Suiza entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 14, 'none', 0),
  (111, 'Mixta media', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 15, 'none', 0),
  (111, 'Mixta entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 16, 'none', 0),
  (111, 'Ranchera media', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 17, 'none', 0),
  (111, 'Ranchera entera', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 18, 'none', 0),
  (111, 'Chori pollo media', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 19, 'none', 0),
  (111, 'Chori pollo entera', 24000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 20, 'none', 0),
  (111, 'Chori cerdo media', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 21, 'none', 0),
  (111, 'Chori cerdo entera', 24000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 22, 'none', 0),
  (111, 'Chori suizo media', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 23, 'none', 0),
  (111, 'Chori suizo entera', 24000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 24, 'none', 0),
  (111, 'De la casa media', 20000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-media.jpg', true, 25, 'none', 0),
  (111, 'De la casa entera', 25000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/desgranado-entera.jpg', true, 26, 'none', 0);

-- Asados
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (112, 'Chori casero entero', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-entero.jpg', true, 1, 'none', 0),
  (112, 'Pechuga medio', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-medio.jpg', true, 2, 'none', 0),
  (112, 'Pechuga entero', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-entero.jpg', true, 3, 'none', 0),
  (112, 'Cerdo medio', 14000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-medio.jpg', true, 4, 'none', 0),
  (112, 'Cerdo entero', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-entero.jpg', true, 5, 'none', 0),
  (112, 'Mixto medio', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-medio.jpg', true, 6, 'none', 0),
  (112, 'Mixto entero', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-entero.jpg', true, 7, 'none', 0),
  (112, 'De la casa medio', 19000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-medio.jpg', true, 8, 'none', 0),
  (112, 'De la casa entero', 23000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/asado-entero.jpg', true, 9, 'none', 0);

-- Cervezas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (113, 'Aguila Original', 4000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/cerveza.jpg', true, 1, 'none', 0),
  (113, 'Aguila Light', 4000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/cerveza.jpg', true, 2, 'none', 0),
  (113, 'Budweiser', 4000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/cerveza.jpg', true, 3, 'none', 0),
  (113, 'Coronita', 4500, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/cerveza.jpg', true, 4, 'none', 0),
  (113, 'Smirnoff', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/cerveza.jpg', true, 5, 'none', 0);

-- Micheladas cerveza
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (114, 'Tradicional', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 1, 'none', 0),
  (114, 'Frutos Rojos', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 2, 'none', 0),
  (114, 'Frutos Verdes', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 3, 'none', 0),
  (114, 'Kiwi', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 4, 'none', 0),
  (114, 'Mango Biche', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 5, 'none', 0),
  (114, 'Maracuyá', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 6, 'none', 0),
  (114, 'Cereza', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 7, 'none', 0),
  (114, 'Fresa', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 8, 'none', 0),
  (114, 'Smirnoff', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-cerveza.jpg', true, 9, 'none', 0);

-- Micheladas soda
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (115, 'Tradicional', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 1, 'none', 0),
  (115, 'Frutos Rojos', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 2, 'none', 0),
  (115, 'Frutos Verdes', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 3, 'none', 0),
  (115, 'Manzana Verde', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 4, 'none', 0),
  (115, 'Kiwi', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 5, 'none', 0),
  (115, 'Mango Biche', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 6, 'none', 0),
  (115, 'Cereza', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 7, 'none', 0),
  (115, 'Fresa', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 8, 'none', 0),
  (115, 'Maracuyá', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 9, 'none', 0),
  (115, 'Mandarina', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 10, 'none', 0),
  (115, 'Maracumango', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/michelada-soda.jpg', true, 11, 'none', 0);

-- Jugos granizados
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (116, 'Tamarindo en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 1, 'none', 0),
  (116, 'Frutos Rojos en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 2, 'none', 0),
  (116, 'Níspero en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 3, 'none', 0),
  (116, 'Milo en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 4, 'none', 0),
  (116, 'Coco en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 5, 'none', 0),
  (116, 'Fresa en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 6, 'none', 0),
  (116, 'Maracuyá en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 7, 'none', 0),
  (116, 'Mora en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 8, 'none', 0),
  (116, 'Guanábana en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 9, 'none', 0),
  (116, 'Zapote en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 10, 'none', 0),
  (116, 'Mandarina en agua', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 11, 'none', 0),
  (116, 'Tamarindo en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 12, 'none', 0),
  (116, 'Frutos Rojos en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 13, 'none', 0),
  (116, 'Níspero en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 14, 'none', 0),
  (116, 'Milo en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 15, 'none', 0),
  (116, 'Coco en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 16, 'none', 0),
  (116, 'Fresa en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 17, 'none', 0),
  (116, 'Maracuyá en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 18, 'none', 0),
  (116, 'Mora en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 19, 'none', 0),
  (116, 'Guanábana en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 20, 'none', 0),
  (116, 'Zapote en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 21, 'none', 0),
  (116, 'Mandarina en leche', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/granizado.jpg', true, 22, 'none', 0);

-- Limonadas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (117, 'Tradicional', 8000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/limonada.jpg', true, 1, 'none', 0),
  (117, 'Cerezada', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/limonada.jpg', true, 2, 'none', 0),
  (117, 'Brasileña', 10000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/limonada.jpg', true, 3, 'none', 0),
  (117, 'Limonada de coco', 12000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/limonada.jpg', true, 4, 'none', 0);

-- Mocktails
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (118, 'Eléctrica', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/mocktail.jpg', true, 1, 'none', 0),
  (118, 'Océano', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/mocktail.jpg', true, 2, 'none', 0),
  (118, 'Barbie', 9000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/mocktail.jpg', true, 3, 'none', 0);

-- Cocteles
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (119, 'Margarita Fresa', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 1, 'none', 0),
  (119, 'Margarita Maracuyá', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 2, 'none', 0),
  (119, 'Margarita de Coco', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 3, 'none', 0),
  (119, 'Tequila Sunrise', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 4, 'none', 0),
  (119, 'Bandolera', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 5, 'none', 0),
  (119, 'Mojito Tradicional', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 6, 'none', 0),
  (119, 'Mojito Fresa', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 7, 'none', 0),
  (119, 'Mojito Maracuyá', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 8, 'none', 0),
  (119, 'Daikiri Fresa', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 9, 'none', 0),
  (119, 'Cuba Libre', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 10, 'none', 0),
  (119, 'Tinto de Verano', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 11, 'none', 0),
  (119, 'Sangría Española', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 12, 'none', 0),
  (119, 'Beso Blanco', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 13, 'none', 0),
  (119, 'Michelada Endiablada', 18000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 14, 'none', 0),
  (119, 'Piña Colada', 17000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/coctel.jpg', true, 15, 'none', 0);

-- Bebidas
insert into products (category_id, name, price, description, image_url, available, sort_order, stock_mode, stock) values
  (120, 'Hatsu', 6000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/bebida.jpg', true, 1, 'none', 0),
  (120, 'Soda Bretaña', 3000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/bebida.jpg', true, 2, 'none', 0),
  (120, 'Canada Dry', 4000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/bebida.jpg', true, 3, 'none', 0),
  (120, 'Happy Birthday', 15000, null, 'https://xpvipclordobiguqjihh.supabase.co/storage/v1/object/public/product-images/menu/bebida.jpg', true, 4, 'none', 0);

-- 4) ADICIONALES de la carta (siempre disponibles: stock 9999)
--    (borra primero los de una ejecucion anterior, para no duplicar)
delete from addon_categories where addon_id in (select id from addons where name in ('Salchicha', 'Mainguera', 'Maiz tierno', 'Ternera', 'Butifarra Casero', 'Cerdo', 'Pollo', 'Suizo', 'Ranchero', 'Gratinado', 'Papas francesa'));
delete from addons where name in ('Salchicha', 'Mainguera', 'Maiz tierno', 'Ternera', 'Butifarra Casero', 'Cerdo', 'Pollo', 'Suizo', 'Ranchero', 'Gratinado', 'Papas francesa');

insert into addons (name, price, stock, active) values
  ('Salchicha', 1000, 9999, true),
  ('Mainguera', 2000, 9999, true),
  ('Maiz tierno', 4000, 9999, true),
  ('Ternera', 5000, 9999, true),
  ('Butifarra Casero', 5000, 9999, true),
  ('Cerdo', 5000, 9999, true),
  ('Pollo', 6000, 9999, true),
  ('Suizo', 6000, 9999, true),
  ('Ranchero', 6000, 9999, true),
  ('Gratinado', 6000, 9999, true),
  ('Papas francesa', 6000, 9999, true)

;

-- enlazados a TODAS las categorias de comida (101-112)
insert into addon_categories (addon_id, category_id)
select a.id, c.id
from addons a cross join categories c
where a.name in ('Salchicha', 'Mainguera', 'Maiz tierno', 'Ternera', 'Butifarra Casero', 'Cerdo', 'Pollo', 'Suizo', 'Ranchero', 'Gratinado', 'Papas francesa')
  and c.id between 101 and 112
on conflict do nothing;

-- ============================================================
-- Fin. Verificacion rapida:
--   select c.name, count(*) from products p
--     join categories c on c.id = p.category_id group by 1 order by 2 desc;
-- ============================================================
