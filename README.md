# TypeInferencer

El objetivo de este proyecto es la implementación de un intérprete de COOL que permita la inferencia de tipos a partir del uso de AUTO_TYPE. Para el desarrollo del mismo se utilizaron como base los contenidos vistos en Clase Práctica durante el curso de Compilación.

### Requerimientos 📋

El proyecto fue desarrollado haciendo uso de:

- `python v-3.7.2`
- `streamlit v-0.56.0`

Se necesita también algún navegador web instalado como `chrome` o `firefox`

### Modo de uso

Para ejecutar solamente abra la consola tal que la dirección raíz sea la del fichero donde se encuentra el proyecto y ejecute la siguiente línea:

```
streamlit run main.py
```

Para insertar el texto que representará el código de COOL debe tener en cuenta las reglas de sintaxis de este lenguaje. En caso contrario, ya sea durante el proceso del lexer o de parsing, obtendrá un error que será reportado y no se llevará a cabo ningún análisis posterior. Si el texto es sintácticamente correcto de acuerdo a Cool, se mostrarán los errores semánticos, si los hay, y se mostrará el árbol resultante del análisis donde todos los AUTO_TYPES habrán sido reemplazados por el tipo estático inferido.

Si un AUTO_TYPE es usado de forma incorrecta, este no se verá sustituido en la salida del programa; no obstante el error sí es reportado.

### Pipeline

Una vez terminada la fase de *parsing* se llevan a cabo los siguientes pasos:

- Recolección de tipos
- Construcción de tipos
- Chequeo / Inferencia de tipos

A continuación se explicará el funcionamiento de cada uno:

#### Recolección de tipos

Esta fase se realiza mediante la clase *Type Collector* que sigue los siguientes pasos:

- Definición de los *built-in types*, o sea, los tipos que son inherentes al lenguaje Cool : Int, String, Bool, IO, Object; incluyendo la definición de sus métodos. Además se añaden como tipos SELF_TYPE, AUTO_TYPE.
- Recorrido por las declaraciones hechas en el programa recolectando los tipos creados.
- Chequeo de los padres que están asignados a cada tipo. Como las clases pueden definirse de modo desordenado, el chequeo de la asignación correcta de padres para cada clase debe hacerse después de recolectar los tipos. De esta forma es posible capturar errores como que un tipo intente heredar de otro que no existe. Aquellas clases que no tengan un padre explícito se les asigna Object como padre.
- Chequeo de herencia cíclica. En caso de detectar algún ciclo en la jerarquía de tipos, se reporta el error, y a la clase por la cual hubo problema se le asigna Object como padre, para continuar el análisis.
- Una vez chequeados los puntos anteriores, se reorganiza la lista de nodos de declaración de clases que está guardada en el nodo Program. La reorganización se realiza tal que para cada tipo A, si este hereda del tipo B (siendo B otra de las clases definidas en el programa) la posición de B en la lista es menor que la de A. De esta manera, cuando se visite un nodo de declaración de clase, todas las clases de las cuales él es descendiente, ya fueron visitadas previamente.

#### Construcción de tipos

La construcción de tipos se desarrolla empleando la clase Type Builder. Esta se encarga de visitar los *features* de las declaraciones de clase, dígase: funciones y atributos; tal que cada tipo contenga los atributos y métodos que lo caracterizan.

Además se encarga de chequear la existencia del tipo Main con su método main correspondiente, como es requerido en COOL.

En esta clase también se hace uso de la clase Inferencer Manager que permitirá luego realizar la inferencia de tipo. Por tanto, a todo atributo, parámetro de método o tipo de retorno de método, que esté definido como AUTO_TYPE se le asigna un *id* que será manejado por el manager mencionado anteriormente. Este id será guardado en el nodo en cuestión para poder acceder a su información en el manager cuando sea necesario.

#### Chequeo e Inferencia de tipos

En primer lugar se utiliza la clase Type Checker para validar el correcto uso de los tipos definidos. Toma la instancia de clase Inferencer Manager utilizada en el Type Builder para continuar la asignación de id a otros elementos en el código que también pueden estar definidos como AUTO_TYPE, como es el caso de las variables definidas en la expresión Let. Las variables definidas en el Scope se encargarán de guardar el id asignado; en caso de que no se les haya asignado ninguno, el id será *None*.

La instancia de Scope creada en el Type Checker, así como la de Inferencer Manager se pasarán al Type Inferencer para realizar la inferencia de tipos.

Ahora bien, la clase Inferencer Manager guarda las listas *conforms_to*, *conformed_by*, *infered_type*. El id asignado a una variable representa la posición donde se encuentra la información relacionada a la misma en las listas.

Sea una variable con id = i, que está definida como AUTO_TYPE y sea A el tipo estático que se ha de inferir:

- `conforms_to[i]` guarda una lista con los tipos a los que debe conformarse A; note que esta lista contiene al menos al tipo Object. El hecho de que A se conforme a estos tipos, implica que todos ellos deben encontrarse en el camino de él a Object en el árbol de jerarquía de tipos. En caso contrario se puede decir que hubo algún error en la utilización del AUTO_TYPE para esta variable. Sea B el tipo más lejano a Object de los que aparecen en la lista.
- `conformed_by[i]` almacena una lista con los tipos que deben conformarse a A. Luego el menor ancestro común (*LCA - Lowest Common Ancestor*) de dichos tipos deberá conformarse a A. Note que este siempre existirá, pues en caso peor será Object, que es la raíz del árbol de tipos. Sea C el LCA de los tipos guardados. Note que si la lista está vacía, (que puede suceder) C será *None*.
- Como C se conforma a A y A se conforma B, tiene que ocurrir que C se conforma a B. En caso contrario, se reporta un uso incorrecto de AUTO_TYPE para esa variable. Todos los tipos en el camino entre B y C son válidos para inferir A; pues cumplen con todas las restricciones que impone el programa. En nuestro caso se elige C, que es el tipo más restringido, para la inferencia. En caso de que C sea *None* se toma B como tipo de inferencia.
- `infered_type[i]` guardará el tipo inferido una vez realizado el procedimiento anterior; mientra tanto su valor es *None*.

La clase Inferencer Manager además, está equipada con métodos para actualizar las listas dado un id, y para realizar la inferencia dados los tipos almacenados.

El Type Inferencer por su parte, realizará un algoritmo de punto fijo para llevar a cabo la inferencia:

1. Realiza un recorrido del AST (Árbol de Sintaxis Abstracta) actualizando los conjuntos ya mencionados. Cuando se visita un nodo, específicamente un *ExpressionNode*, este recibe como parámetro un conjunto de tipos a los que debe conformarse la expresión; a su vez retorna el tipo estático computado y el conjunto de tipos que se conforman a él. Esto es lo que permite actualizar las listas que están almacenadas en el *manager*.
2. Infiere todos los tipos que pueda con la información recogida.
3.  - Si pudo inferir al menos uno nuevo, regresa al punto 1; puesto que este tipo puede influir en la inferencia de otros.
    - Si no pudo inferir ninguno, significa que ya no hay más información que se pueda inferir, por tanto se realiza un último rerrido asignando tipo Object a todos los AUTO_TYPES que no pudieron ser inferidos.

> Se considera que un tipo puede ser inferido, si no ha sido inferido anteriormente, y si su lista *conforms_to* contiene a otro tipo distinto de Object o su lista *conformed_by* contiene al menos un tipo.

Por último se realiza un nuevo recorrido del AST con el Type Checker para detectar nuevamente los errores semánticos que puedan existir en el código, ahora con los AUTO_TYPES sustituidos por el tipo inferido.

## Autores ✒️

- **Carmen Irene Cabrera Rodríguez** - [cicr99](https://github.com/cicr99)
- **Enrique Martínez González** - [kikeXD](https://github.com/kikeXD)

## Licencia

Este proyecto se encuentra bajo la Licencia (MIT License) - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.
