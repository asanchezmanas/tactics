# Seguridad de Datos: Integración con Internxt

En **Tactics**, la privacidad y la soberanía de sus datos no son negociables. Por ello, hemos integrado nuestro sistema de copias de seguridad con **Internxt**, el líder europeo en almacenamiento en la nube ultra-seguro.

## ¿Por qué Internxt?

A diferencia de los proveedores tradicionales, Internxt ofrece una infraestructura de **Conocimiento Cero (Zero-Knowledge)**. Esto significa que sus datos se cifran en el origen (nuestro servidor) antes de ser enviados a la nube. **Nadie**, ni siquiera Internxt o Tactics, puede acceder al contenido de sus archivos sin su clave privada.

### Pilares de Seguridad

1. **Cifrado Militar (AES-256-GCM)**: Utilizamos los estándares de cifrado más robustos de la industria para proteger sus archivos CSV crudos y los estados de los modelos de IA.
2. **Soberanía Europea**: Sus datos se almacenan en infraestructuras dentro de la Unión Europea, cumpliendo estrictamente con el **RGPD (GDPR)**.
3. **Fragmentación de Archivos**: Los archivos se dividen en fragmentos que se distribuyen de forma segura, evitando que un único servidor contenga una copia completa de su información.

## ¿Qué datos se protegen?

Tactics utiliza la bóveda segura de Internxt para almacenar:
- **Copias de Seguridad de Ingesta**: Los archivos CSV que usted sube se respaldan de forma cifrada.
- **Instantáneas de Algoritmos**: Los parámetros de sus modelos entrenados (LTV, MMM) se guardan para permitir una recuperación rápida ante cualquier desastre sistémico.
- **Logs de Auditoría**: Registros de actividad para garantizar la trazabilidad total del sistema.

## Beneficios para su Empresa

- **Tranquilidad Total**: Sus datos de clientes y ventas están protegidos contra accesos no autorizados.
- **Cumplimiento Legal**: Minimice los riesgos de cumplimiento normativo al usar tecnología específicamente diseñada para el marco legal europeo.
- **Resiliencia Operativa**: En caso de fallo crítico en el servidor principal, Tactics puede restaurar su estado predictivo en minutos utilizando la bóveda de Internxt.

---
*Para más información sobre la arquitectura técnica de este conector, consulte la [Documentación Técnica de SecureVault](../technical/ARCHITECTURE_OVERVIEW.md).*
