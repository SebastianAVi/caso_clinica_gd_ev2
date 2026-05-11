# TODO - ev2_clinica

- [ ] Revisar y actualizar `etapa1_ingesta.py` para que use `data/raw_origen` si existe y si no, haga fallback a `data/raw` como origen.
- [ ] Añadir una validación para evitar copiar sobre sí mismo si origen y destino coinciden.
- [x] Ejecutar `python etapa1_ingesta.py` y verificar que: 
  - [x] Se cree el log en `logs/`
  - [x] Se reporten los 3 archivos con registros.


