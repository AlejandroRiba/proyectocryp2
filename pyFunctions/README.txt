#############################################   CONCEPTOS   #############################################

TWEAK : 
       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
En palabras simples, el tweak es un valor adicional que se usa junto con la clave para cifrar un dato de forma un poco diferente cada vez, incluso si el valor original y la clave son los mismos.

El tweak es como una especie de "ajuste" o "extra" que se añade al proceso de cifrado. Su propósito es que el mismo dato, cifrado con la misma clave pero con distintos tweaks, tenga resultados diferentes. Esto ayuda a que los cifrados no se vean repetidos ni formen patrones.

Por ejemplo, si se cifran números de tarjeta de crédito con la misma clave:
- Si cambias el tweak, el número de tarjeta cifrado resultará diferente.
- Sin el tweak, el mismo número y la misma clave siempre producirían el mismo cifrado, lo que podría ser menos seguro. 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%