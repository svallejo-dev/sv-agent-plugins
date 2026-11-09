# Acoplamiento de cambio desde git

Lo que cambia junto pertenece junto. La historia de git dice qué cambia junto con más honestidad que un diagrama. La técnica se conoce como análisis de acoplamiento temporal o de cambio (popularizada por Adam Tornhill en _Your Code as a Crime Scene_).

**Analogía:** es mirar qué caminos de tierra se formaron en un parque: muestran por dónde camina la gente de verdad, no por donde el urbanista dibujó las aceras.

## Pares de archivos que cambian juntos

Desde la raíz del repo, últimos 12 meses, ignorando commits de merge:

```bash
git log --since="12 months ago" --no-merges --name-only --pretty=format:'--%h' \
| awk '/^--/{ if (n>1 && n<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print f[i]" | "f[j]; n=0; next }
       NF{ f[++n]=$0 }
       END{ if (n>1 && n<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print f[i]" | "f[j] }' \
| sort | uniq -c | sort -rn | head -30
```

Los commits con más de 30 archivos se ignoran porque suelen ser refactors masivos o formateos que no dicen nada de acoplamiento.

## Agregado por carpeta o servicio

Para ver el acoplamiento entre módulos o servicios en vez de archivos, agrupa por prefijo de carpeta:

```bash
git log --since="12 months ago" --no-merges --name-only --pretty=format:'--%h' \
| awk -F/ 'function flush(){ if (c<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print m[i]" | "m[j]; delete s; n=0; c=0 }
           /^--/{ flush(); next }
           NF>1{ c++; k=$1"/"$2; if(!(k in s)){ s[k]=1; m[++n]=k } }
           END{ flush() }' \
| sort | uniq -c | sort -rn | head -20
```

Ajusta la profundidad (`$1"/"$2`) a la estructura del repo (por ejemplo `internal/<contexto>` o `services/<servicio>`).

## Cómo leerlo

- **Pares dentro del mismo contexto**: esperado; confirma la frontera.
- **Pares entre contextos distintos con mucha frecuencia**: señal de que la frontera corta algo que cambia junto, o de que falta un Published Language y los cambios de esquema se propagan.
- **Entre repositorios**: si dos servicios en repos distintos necesitan PRs coordinados con frecuencia, lo mismo; búscalo en los tickets o en los PRs enlazados.
- Combínalo con el dueño de los datos y con el lenguaje: el acoplamiento de cambio solo es una de las señales, y en un sistema joven tiene poca historia.
