battery set 100
atget id id
set ite 0

data p "hola" id id
send p

loop
inc ite

# Si no recibe mensajes en mucho tiempo, parar
if (ite >= 1000)
	cprint "Base: fin por iteraciones"
	stop
end

# Esperar mensajes con timeout
receive mens 10

# Solo procesar si hay mensaje valido
if(mens != "")
	rdata mens tipo valor1 valor2 sensor ite

	if(tipo == "alerta")
		cprint "Alerta en: longitud " valor1 ", latitud: " valor2 " sensor: " sensor " iteracion " ite 
	end

	if(tipo == "critico")
		cprint "Nodo descargado en: longitud " valor1 ", latitud: " valor2
		data p "stop"
		send p
		wait 1000
		stop
	end
end

delay 10
battery set 100
atget id id
set ite 0

data p "hola" id id
send p

loop
inc ite

# Si no recibe mensajes en mucho tiempo, parar
if (ite >= 1000)
	cprint "Base: fin por iteraciones"
	stop
end

# Esperar mensajes con timeout
receive mens 10

# Solo procesar si hay mensaje válido
if(mens != "")
	rdata mens tipo valor1 valor2 sensor ite

	if(tipo == "alerta")
		cprint "Alerta en: longitud " valor1 ", latitud: " valor2 " sensor: " sensor " iteracion " ite 
	end

	if(tipo == "critico")
		cprint "Nodo descargado en: longitud " valor1 ", latitud: " valor2
		data p "stop"	
		send p
		wait 1000
		stop
	end
end

delay 10
