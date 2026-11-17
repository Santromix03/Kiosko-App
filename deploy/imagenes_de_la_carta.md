# Fotografías de la carta — dónde va cada imagen

La carta ya está cargada en Supabase con la foto **pre-asignada por sección**:
cada producto apunta a una ruta del bucket `product-images` con esta forma:

```
<tu-supabase>/storage/v1/object/public/product-images/menu/<nombre>.jpg
```

Solo tienes que **subir los archivos con el nombre exacto** y la carta del
kiosco muestra las fotos solita. Si un archivo no está, la tarjeta muestra
"Sin imagen" — no rompe nada.

## Paso a paso

1. Abre **Supabase → Storage → bucket `product-images`**.
2. Crea una carpeta dentro que se llame exactamente **`menu`** (minúsculas).
3. Sube los archivos de la tabla de abajo (pueden ser .jpg; si tienes .png,
   renómbralos a .jpg igualmente — el nombre es lo que importa, o cambia la
   extensión en la tabla `products`).
4. En el kiosco toca la **X** y vuelve a entrar (o reinicia la app) para
   refrescar el menú.

## Archivos y su sección

| # | Archivo (en `menu/`) | Sección que cubre |
|---|---|---|

| 1 | `pizza.jpg` | Pizzas (todas: personal y familiar) |
| 2 | `arepa-rellena.jpg` | Arepas rellenas (las 14) |
| 3 | `salchipapa-media.jpg` | Salchipapa — porciones media |
| 4 | `salchipapa-entera.jpg` | Salchipapa — porciones entera |
| 5 | `patacon-relleno.jpg` | Patacones rellenos (los 9) |
| 6 | `hamburguesa.jpg` | Hamburguesas (las 11) |
| 7 | `perro-caliente.jpg` | Perros calientes (los 16) |
| 8 | `sandwich.jpg` | Sandwich (los 13) |
| 9 | `picada-papas-media.jpg` | Picadas papas — media |
| 10 | `picada-papas-entera.jpg` | Picadas papas — entera |
| 11 | `picada-patacon-media.jpg` | Picadas patacón — media |
| 12 | `picada-patacon-entera.jpg` | Picadas patacón — entera |
| 13 | `salvajadas-grandes.jpg` | Salvajadas (las 6) |
| 14 | `desgranado-media.jpg` | Desgranado — media |
| 15 | `desgranado-entera.jpg` | Desgranado — entera |
| 16 | `asado-medio.jpg` | Asados — porción medio |
| 17 | `asado-entero.jpg` | Asados — porción entero |
| 18 | `cerveza.jpg` | Cervezas (las 5) |
| 19 | `michelada-cerveza.jpg` | Micheladas con cerveza (las 9) |
| 20 | `michelada-soda.jpg` | Micheladas en soda o ginger (las 11) |
| 21 | `granizado.jpg` | Jugos granizados (agua y leche, los 22) |
| 22 | `limonada.jpg` | Limonadas (las 4) |
| 23 | `mocktail.jpg` | Mocktail's sin alcohol (las 3) |
| 24 | `coctel.jpg` | Cocteles (los 15) |
| 25 | `bebida.jpg` | Bebidas: Hatsu, Soda Bretaña, Canada Dry, Happy Birthday |

Son **25 archivos** en total.

## Foto distinta para un producto puntual

Si quieres que una hamburguesa concreta tenga su propia foto (en vez de la
genérica de la sección): Panel web → **Productos** → lápiz (editar) →
**Fotografía del producto** → subir → guardar. El panel sube la foto con
nombre propio y actualiza la URL de ese producto; la genérica deja de usar.

## Notas de la transcripción

- **BEBIDAS de la carta de comida (caja con aguas / Postobón / Coca-Cola)**:
  los precios salen borrosos en la foto, así que esa caja **no se cargó**.
  Solo entraron Hatsu, Soda Bretaña, Canada Dry y Happy Birthday (de la carta
  de bebidas). Si me pasas esa caja legible, la agrego.
- En **arepas rellenas**, la línea que se lee "Maita" la cargué como
  **Mixta** ($13.000). Confírmame si está bien.
- Precios que vale la pena revisar contra la carta física:
  **Ranchera** en *Picadas de patacón* ($15.000/$19.000 — en papas es
  igual), y en pizzas las líneas **Ranchera / Buti ranchera**
  ($15.000/$37.000) que en la foto se ven juntas.
- Todos los productos quedaron con **stock_mode 'none'** ("Sin control:
  siempre disponible") y **sin ingredientes/recetas**, como pediste.
- Los **ADICIONALES** de la carta quedaron como adiciones del kiosco
  (stock 9999 = ilimitadas) y aparecen al tocar cualquier producto de comida.

