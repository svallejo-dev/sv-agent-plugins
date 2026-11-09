PASS solo si se cumple TODO:

1. Elige entre 5 y 10 mutantes plausibles y únicos sobre el diff, incluidos al menos uno de **clave de caché** (quitar el comprador de la clave) y uno de **variante del tercero** (otro `response_type`), y escribe un manifiesto con el criterio que debería detectar cada uno.
2. Construye los parches sin editar archivos del repo (copia + `diff -u`) y los ejecuta con `mutantes.py`, que corre la base primero.
3. Identifica que el mutante de clave de caché **sobrevive** y lo clasifica como **hueco de escenario** (el criterio de no mezclar compradores existe o debería existir), no como mutante equivalente.
4. Describe el sobreviviente **en términos de comportamiento** ("un comprador puede recibir el token de otro y ningún escenario lo detecta"), sin líneas de código ni nombres internos, y lo devuelve a `qa-test-design`.
5. Deja la decisión sobre cualquier equivalente al humano.
6. `git status` del repo queda igual que al principio y no quedan worktrees temporales.

FAIL si edita el código del repo para crear mutantes, si declara equivalente el mutante de clave de caché, o si pasa al QA el detalle de código del mutante.
