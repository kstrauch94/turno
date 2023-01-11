### Turno
El programa automaticamente asigna los turnos del mes y año dado. Para cada dia asigna 2 personas para el turno de dia y de noche.
Las siguientes escenarios son evitados:
- Turnos seguidos (dia->noche | noche->dia)
- Turnos de noche en 2 dias contiguos
- Intenta dar la misma cantidad de turnos de dia y noche
- Balancea lo mejor que puede la cantidad de horas extras para cada persona

### Como usar
El programa se abre como cualquier programa ejecutable. El archivo ejecutable ***tiene*** que estar en el mismo folder que el folder __data__ y que el archivo __turno.lp__.

En el folder __data__ se encuentran 4 archivos. El archivo **nombres** tiene una lista de nombres(o apellidos), cada uno en una nueva linea. No se aceptan caracteres especiales, como la "ñ".

Al empezar el programa se tiene que entrar el mes, año y, si aplica, dias feriados(separados por una coma).

Despues de un tiempo, se puede detener el programa. Si se encontre una solucion, se crea un archivo con el nombre **mes-año.xlsx**(Substituyendo el mes y año con los valores dados).

### Condiciones especiales

El archivo **no-juntos** tiene una lista de nombres similar a la de **nombres**. Los nombres en esta lista nunca seran puestos en el mismo turno.

El archivo **dias-bloqueados** tiene una lista de nombres seguidos de dos numeros. Los numeros defines un rango de dias en los que esta persona no sera puesta en turno(de dia o noche).
Por ejemplo, si la linea __talavera,5,7__ esta en el archivo, talavera no sera puesto en ningun turno del 5 al 7 del mes.

#### Archivo "especiales"

El archivo especiales se usa para definir ciertos restricciones a la asignacion de turnos.
Las restricciones son las siguientes:
- ***constraint,type_count,nombre,tipo-dia,turno,cantidad***
- ***constraint,at_most_once_a_week,nombre,tipo-dia***
- ***constraint,fixed,nombre,turno,fecha***
- ***constraint,blocked_shift,nombre,turno,fecha***
- ***exception,even_distribution,nombre***
- ***special_days,nombre,cantidad***

__nombre__ tiene que ser un nombre que se encuentre en el archivo ***nombres*** en el folder ***data***. __cantidad__ es algun numero entero. __turno__ puede ser **day**(dia) o **night**(noche). __tipo-dia__ puede ser **weekday**(dia de semana), **sat**(sabado) o **sun**(domingo). __fecha__ puede ser cualquier fecha del mes(numero entero).


La restriccion ***constraint,type_count,nombre,tipo-dia,turno,cantidad*** se ocupa para asignar a una persona, dada por __nombre__ una cierta cantidad de turnos, dado por __cantidad__, de dia o de noche, dado __turno__ para un cierto tipo de dia, dado por __tipo-dia__. __turno__ es opcional.


Por ejemplo, ***constraint,type_count,talavera,weekday,night,4*** describe que a talavera se le tiene que dar 4 turnos en dia de semana.

La restriccion ***constraint,at_most_once_a_week,nombre,tipo-dia*** se ocupa para decir que se puede asigna un maximo de 1 vez por semana un turno para la persona dada en: dia de semana, sabado o domingo.

Por ejemplo, ***constraint,at_most_once_a_week,talavera,weekday*** describe que a talavera se le asigna maximo 1 turno en dia semana. Note que esto no detiene que talavera tenga un turno un dia de semana y un sabado (o domingo) en la misma semana.

La restriccion ***constraint,fixed,nombre,turno,fecha*** se ocupa para fijar el turno para la persona dada en la fecha especificada.

Por ejemplo ***constraint,fixed,talavera,night,24*** describe que a talavera se le tiene que asignar turno de noche el 24 del mes.

La restriccion ***constraint,blocked_shift,nombre,turno,fecha*** se ocupa para bloquear el turno dado(dia o noche) de la persona y fecha especificadas.

Por ejemplo, ***constraint,blocked_shift,arguello,day,18*** describe que arguello no va a tener turno de dia el 18 del mes.

La restriccion ***exception,even_distribution,nombre*** se ocupa para que la persona dada no tenga garantizado una distribucion igual de turnos de dia y noche.

Por ejemplo, ***exception,even_distribution,talavera*** describe que talavera puede tener 6 turnos de dias y 0 de noche. Sin esta restriccion, la distribucion de turnos seria 3 de dia y 3 de noche.

La restriccion ***special_days,nombre,cantidad*** se ocupa para que la persona dada tenga exactamente la cantidad de turnos dados por mes.

Por ejemplo, ***special_days,talavera,6*** describe que talavera tiene exactamente 6 turnos en el mes.






