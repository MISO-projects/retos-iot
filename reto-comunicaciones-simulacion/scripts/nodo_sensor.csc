set ant 999
set ite 0
set critico 0
battery set 100

atget id id
getpos2 lonSen latSen
atnd n vecinos
cprint "Sensor " id " vecinos: " n " -> " vecinos

loop
inc ite
print ite

# Verificar limite de iteraciones
if (ite >= 1000)
	cprint "Iteraciones sensor: " id " en " ite
	stop
end

# Leer mensajes pendientes
receive mens 10

# Solo procesar si hay mensaje valido
if(mens != "")
	rdata mens tipo valor

	if((tipo=="hola") && (ant == 999))
		set ant valor
		data mens tipo id
		send mens * valor
	end

	if(tipo=="alerta")
		send mens ant
	end

	if (tipo=="stop")
		data mens "stop"
		send mens * valor
		cprint "Para sensor: " id
		wait 1000
		stop
	end
end

# Verificar bateria (solo una vez)
battery bat
if(bat<5)
	if(critico == 0)
		set critico 1
		data mens "critico" lonSen latSen
		send mens ant
		cprint "Bateria critica sensor: " id " bat: " bat
	end
	stop
end

# Esperar 10ms entre transmisiones
delay 10

# Leer sensor de temperatura
areadsensor tempSen
if(tempSen != "X")
	rdata tempSen SensTipo idSens temp
	
	if(temp>30)
		data mens "alerta" lonSen latSen id ite
		send mens ant
	end
end
set ant 999
set ite 0
set critico 0
battery set 100

atget id id
getpos2 lonSen latSen
atnd n vecinos
cprint "Sensor " id " vecinos: " n " -> " vecinos

loop
inc ite
print ite

# Verificar límite de iteraciones
if (ite >= 1000)
	cprint "Iteraciones sensor: " id " en " ite
	stop
end

# Leer mensajes pendientes
receive mens 10

# Solo procesar si hay mensaje válido
if(mens != "")
	rdata mens tipo valor

	if((tipo=="hola") && (ant == 999))
		set ant valor
		data mens tipo id
		send mens * valor
	end

	if(tipo=="alerta")
		send mens ant
	end

	if (tipo=="stop")
		data mens "stop"
		send mens * valor
		cprint "Para sensor: " id
		wait 1000
		stop
	end
end

# Verificar batería (solo una vez)
battery bat
if(bat<5)
	if(critico == 0)
		set critico 1
		data mens "critico" lonSen latSen
		send mens ant
		cprint "Bateria critica sensor: " id " bat: " bat
	end
	stop
end

# Esperar 10ms entre transmisiones
delay 10

# Leer sensor de temperatura
areadsensor tempSen
if(tempSen != "X")
	rdata tempSen SensTipo idSens temp
	
	if(temp>30)
		data mens "alerta" lonSen latSen id ite
		send mens ant
	end
end
