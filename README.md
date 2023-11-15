COMO QUE 33:
----------------

Nuestro proyecto se basa en una aplicación para consultar toda la información posible y actualizada sobre la fórmula 1. Esto incluye tanto pilotos, como circuitos, como escuderías, así como todos los datos relativos a estos. Además mostraremos para cada búsqueda videos de youtube relacionados con esta busqueda que vayamos a realizar.

Funcionalidades:
  * Soporte multiusuario. El usuario introduce el nombre de usuario y su contraseña en los campos correspondientes. Una vez cubiertos, el usuario clica el botón de "Iniciar sesión".
  * Visualizar las carreras restantes del año, así como la fecha, lugar y número de carrera. El usuario no tendrá que introducir ningún dato, solamente clicar en el botón "Calendar"
  * Visualizar la clasificación de cada mundial en función del año introducido por el usuario. El usuario tendrá que clicar en el botón "Classification", elegir un año en el que se haya celebrado la F1 y clicar el botón de búsqueda.
  * Visualizar datos sobre pilotos. El usuario deberá clicar en el botón "Driver", donde podrá elegir el nombre del piloto y clicar en el botón de búsqueda.
  * Visualizar datos de cada gran premio. El usuario deberá clicar en el botón "GP info", donde podrá elegir un gran premio, un año de celebración y clicar en el botón de búsqueda. Se podrá ver una imagen, información general del Gran Premio y la clasificación de la carrera.
  * Ver información de un piloto en una determinada carrera. Desde el apartado de grandes premios, el usuario deberá elegir un piloto que haya participado en ese gran premio y darle al botón de búsqueda para obtener información de sus vueltas en ese gran premio e información de su coche. 
  * Comparar las vueltas de dos pilotos en un determinado gran premio. El usuario deberá clicar en el botón "Charts", elegir dos pilotos, un gran premio, un año y clicar en el botón de búsqueda para obtener un gráfico comparador de las vueltas entre ambos pilotos.
  * Visualizar la velocidad máxima del piloto en cada sector del gran premio. El usuario deberá clicar en el botón "Charts", elegir un piloto, un gran premio, un año y clicar en el botón de búsqueda para obtener un gráfico de la velocidad máxima del piloto en cada sector del gran premio.

Integrantes Grupo:
------------------

  * Raúl Fernández del Blanco r.delblanco@udc.es
  * Armando Martínez Noya a.mnoya@udc.es
  * Brais González Piñeiro brais.gonzalezp@udc.es
  
Cómo ejecutar:
--------------

Secuencia de comandos lanzar la aplicación:

Primero, corremos el container con CONTRL+P -> rebuild container en la terminal de vstudio. Una vez abierta la conexión con el container hacemos los siguientes comandos.
  
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000 

Para ejecutar los tests tendremos que ejecutar el siguiente comando:

    python manage.py test Como33.test.test_views

Problemas conocidos:
--------------------

Lista con los problemas conocidos si los hubiere:

  * Los tiempos de carga en algunos apartados son relativamente altos en las primeras interacciones con la aplicación, porque los datos no están escritos en la caché de la api. Una vez introducidos estos datos en la caché, estos tiempos de carga son mucho mas cortos.
