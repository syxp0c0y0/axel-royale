# Axel's Royale

Duelo de construcción y disparos (estilo 1v1.lol/Fortnite) con progresión: monedas, Pase de Batalla con XP, tienda de cosméticos, perfil, desafíos diarios/semanales, y varios modos contra bots (con un interruptor Ranked ON/OFF). Incluye multijugador online **real**: 1v1 o 2v2, y Ranked Dúos/Tríos junto a 1-2 amigos reales contra equipos de bots, con jugadores reales conectados desde casas distintas.

## Qué incluye

- `server.py` — servidor Python (aiohttp) que sirve la página y actúa de "sala" de emparejamiento para el online (1v1, 2v2 o Ranked con amigos): agrupa hasta 4 sockets por sala (con código al azar o uno personalizado), reenvía sus mensajes entre sí, y también deja que otros sockets se sumen como espectadores (reciben todo, no cuentan para el cupo, nunca controlan nada) — no simula el juego, cada jugador controla su propio personaje.
- `static/index.html` — el juego completo (un solo archivo HTML/CSS/JS, sin dependencias externas aparte de las fuentes de Google).
- `requirements.txt` — la única dependencia (`aiohttp`).

## Probarlo ahora mismo (en tu compu)

```bash
cd arena-de-bloques-online
python3 -m pip install -r requirements.txt
python3 server.py
```

Abre `http://localhost:8080` en el navegador. Para jugar con alguien en la misma red (wifi de casa), esa persona puede abrir `http://TU-IP-LOCAL:8080` en su propio dispositivo — la sala online funciona igual.

## Jugar con alguien desde otra casa (internet) — URL permanente

Para que dos o más personas en redes distintas se conecten, el servidor necesita una URL pública. **No uses un túnel rápido de Cloudflare (`cloudflared tunnel --url ...`, `trycloudflare.com`) para esto** — ese modo es intencionalmente efímero: genera un subdominio nuevo cada vez que se relanza, y no hay forma de fijarlo (así funciona el producto, no es algo que se pueda configurar). Para una URL que **nunca cambia**, hay que desplegar en una plataforma real:

### Render.com — un solo dominio para siempre

El repo ya incluye `render.yaml`, así que Render puede configurar el servicio solo.

1. Crea una cuenta gratis en [render.com](https://render.com) (puedes entrar directo con tu cuenta de GitHub).
2. Sube esta carpeta a un repositorio de GitHub:
   ```bash
   git remote add origin https://github.com/TU-USUARIO/axels-royale.git
   git branch -M main
   git push -u origin main
   ```
   (el repo local y el primer commit ya están hechos — solo falta crear el repo vacío en GitHub y conectarlo con esos dos comandos).
3. En Render: **New → Blueprint**, elige ese repositorio. Render lee `render.yaml` y configura solo el build (`pip install -r requirements.txt`) y el arranque (`python server.py`) — solo hay que confirmar el nombre del servicio (ese nombre define tu URL) y darle a **Apply**.
   - Alternativa manual si prefieres no usar el blueprint: **New → Web Service** → conecta el repo → Build Command `pip install -r requirements.txt` → Start Command `python server.py`.
4. Cuando termine el primer deploy, Render te da una URL fija: `https://<nombre-que-elegiste>.onrender.com`. **Esa es tu URL canónica** — no vuelve a cambiar.
5. Comparte esa URL con tus rivales — todos la abren, uno crea sala (1v1, 2v2 o Ranked con amigos) y los demás se unen con el código.

**Cómo actualizar el juego sin nunca cambiar la URL**: cada vez que quieras publicar cambios, simplemente:
```bash
git add -A
git commit -m "lo que cambiaste"
git push
```
Render detecta el push al repo conectado y vuelve a desplegar automáticamente **sobre el mismo servicio** — la URL sigue siendo exactamente la misma. Nunca crees un servicio nuevo en Render para una actualización; usa siempre este mismo repo/servicio.

Las rutas internas del juego (todo vive en `static/index.html`, sin rutas de servidor adicionales aparte de `/` y `/ws`) ya sirven todas desde ese único dominio — no hay múltiples deployments que coordinar.

> El plan gratuito de Render "duerme" el servicio tras un rato sin uso; la primera carga después de eso tarda unos 30-50 segundos en despertar. Es normal, y no afecta la URL.

### Alternativas equivalentes (mismo principio: un dominio fijo por servicio)

- **Railway.app** o **Fly.io** — mismo esquema (Python + `aiohttp`, comando de inicio `python server.py`), también con una URL de producción fija por proyecto que no cambia entre despliegues.
- **Túnel con nombre de Cloudflare + dominio propio**: si ya tienes un dominio, un *named tunnel* de Cloudflare (no el modo "quick") ligado a una cuenta sí puede mapearse permanentemente a `axels-royale.tudominio.com` — a diferencia del túnel rápido, este no cambia de hostname.
- **Un servidor propio / VPS** — corre `python3 server.py` (define la variable `PORT` si quieres otro puerto) detrás de Nginx o directamente expuesto; el dominio lo defines tú y es fijo por naturaleza.

## Modos de juego

- **Práctica libre** — sin rival, munición y materiales infinitos.
- **1v1 · Bot** (Fácil / Normal / Difícil) — contra un solo bot, local, sin servidor.
- **2v2 · Contra Bots** — tú + 1 bot aliado vs 2 bots rivales, todo local (sin servidor).
- **Multijugador online** — desde el lobby (botón MULTIJUGADOR ONLINE dentro de JUGAR) puedes **crear sala 1v1** (2 jugadores reales) o **crear sala 2v2** (4 jugadores reales, 2 equipos de 2). El anfitrión elige el tipo de sala; el resto solo escribe el código y se une. En ambos, fuego amigo está desactivado entre compañeros de equipo.
  - **Código personalizado**: al crear cualquier sala (online normal o Ranked con amigos) puedes escribir tu propio código (3-10 letras/números) en vez de que el servidor invente uno al azar — así puedes reusar siempre el mismo con el mismo grupo, sin tener que volver a compartirlo cada vez. Si ya está en uso, el servidor te avisa para que pruebes otro.
  - **Salas recientes**: el navegador recuerda los últimos códigos que creaste o usaste (por navegador, vía `localStorage`) y los muestra como chips debajo del campo para unirse — un clic y ya está escrito, sin tener que recordarlo de memoria.
  - **Lobby de pre-partida**: en cuanto la sala se llena, antes de que empiece la partida aparecen unos segundos con la alineación del equipo — cada jugador conectado se ve con su skin/sombrero/halo realmente equipados (mismo render que usa CUSTOMIZE, nada inventado para la vista previa) y su insignia de rango junto al nombre.
  - **Ping/marcador de equipo**: clic central del mouse (o tecla `G`) coloca una marca visible solo para tu equipo en el punto señalado, con tu nombre debajo — útil para avisar posiciones en 2v2 o Ranked con amigos sin necesidad de voz.
  - **Modo espectador**: desde el mismo lobby, con el código de cualquier sala (normal o Ranked) puedes entrar solo a mirar, sin jugar — ves el mismo mapa y a todos los jugadores en tiempo real, con `Tab` para cambiar a quién sigue la cámara. No participa en la partida ni afecta el resultado de nadie.

En cualquier modo por equipos (2v2 local o 2v2 online), los bots/compañeros reconocen aliados/enemigos, buscan cobertura al estar heridos, recogen Mini Shields/Med Kits del mapa y se los aplican cuando conviene, y persiguen al enemigo vivo más cercano (cambiando de objetivo si aparece uno más próximo).

**Construcción**: solo existe el **Muro** (`Q`) — rampa, cono y suelo se quitaron porque en una cámara cenital no aportaban nada (no hay nada que escalar ni asomarse). El mapa se sortea al azar entre **6 diseños de cobertura** en cada partida — Clásico, Cruce e Islas (los originales) más **Fortaleza** (una fortaleza hueca justo en el centro, con entrada solo por norte o sur — peleas cerradas adentro, líneas de tiro largas afuera), **Laberinto** (bandas de muros cortos escalonados por todo el mapa, sin ningún carril recto — combate cercano constante) y **Centro** (un punto de control abierto en medio, con carriles de cobertura convergiendo desde los 4 lados). El sorteo evita repetir el mismo mapa dos veces seguidas cuando hay otros disponibles, y en Ranked con amigos/espectador el mapa sigue siendo idéntico para todos los que están en la sala (se decide con la misma semilla del código de sala).

**Minimapa** (esquina superior derecha): versión reducida del terreno real de la partida (mismo arte que el mapa grande, solo escalado), con los obstáculos marcados, tu posición como una flecha que apunta hacia donde apuntas, y tus compañeros vivos como puntos — se actualiza en vivo. En Ranked también dibuja el círculo de la zona. Los rivales/bots **nunca** aparecen ahí a propósito, para no convertirlo en un radar gratis.

**Mapa**: cada partida genera un terreno propio (no solo el diseño de cobertura) — zonas de tierra, arena y una laguna repartidas por el mapa, un par de caminos que las conectan, y árboles/arbustos/piedras decorativos esparcidos sobre el pasto. Todo eso es puramente visual (no bloquea disparos ni movimiento), para que el mapa se sienta vivo sin tocar el gameplay ya probado. Además de las cajas (crates) de siempre, cada partida coloca 2-3 pequeñas "casitas" (una estructura hueca de 3x3 con una entrada) como cobertura destructible extra — usan exactamente el mismo sistema de colisión/vida que las crates, solo con otra forma y color, así que son un punto de cobertura real, no decoración.

## Lobby y navegación

Menú principal rediseñado como un lobby real (interfaz original, no una copia de Fortnite):

- **Barra superior fija** con las 6 secciones, en este orden: **LOBBY → BATTLE PASS → CHALLENGES → LOCKER → ITEM SHOP → PROFILE** — siempre visible en las 6, con la sección activa resaltada y el contador de desafíos reclamables junto a CHALLENGES.
- **Lobby**: tu personaje centrado, con el color/sombrero/halo que tengas equipados de verdad (se actualiza al instante si cambias algo en LOCKER, sin recargar), tu insignia de rango actual junto a tu nombre, y un fondo que se tiñe con el color de tu propio rango. Incluye una fila de "equipo" (tú + un espacio "+ Amigos · Próximamente" reservado para cuando exista ese sistema — no es un botón que finja funcionar, es espacio guardado a propósito). Termina en: modo seleccionado + CAMBIAR MODO, el botón JUGAR, y monedas/bajas/victorias — sin tarjetas repetidas de Desafíos/Pase/Ranked/Modo clásico abajo (esos accesos ya viven en la barra superior o dentro de Cambiar modo).
- **Ranked con amigos reales y multijugador online**: ya no tienen su propia tarjeta en el Lobby — se llega a ellos desde dos enlaces dentro de la ventana "Cambiar modo" ("¿Jugar con amigos reales o ver el leaderboard?" y "¿Multijugador online real?"), exactamente donde vive todo lo demás relacionado con Ranked/Clásico.
- **Selector de modo**: el botón "CAMBIAR MODO" abre una ventana con tres secciones — **BATTLE ROYALE** (Solo/Dúos/Tríos, cada uno con su propio interruptor **RANKED: ACTIVADO/DESACTIVADO**), **COMBATE / ARENA** (1v1, con su dificultad Fácil/Normal/Difícil de siempre como chips dentro de la misma tarjeta, y 2v2) y **PRÁCTICA** (Práctica libre) — eliges una, confirmas, y vuelves al Lobby viendo el modo (y el estado de Ranked) elegidos; Cancelar no cambia nada. El botón **JUGAR** siempre inicia una partida en el modo actualmente seleccionado.
- **Ranked ON/OFF** (solo aplica a Solo/Dúos/Tríos): con Ranked desactivado juegas exactamente la misma partida — mismos bots, misma zona/storm, misma dificultad — pero sin costo de entrada y sin que el resultado toque tu rango ni tus puntos competitivos; el HUD y la pantalla de resultados lo dejan claro ("PARTIDA NORMAL — no afecta tu rango") en vez de mostrar un confuso "+0". Con Ranked activado, todo funciona exactamente como siempre. El modo Ranked con amigos reales (ver más abajo) no tiene este interruptor — esas partidas siempre puntúan.

## Ranked Battle Royale

Modo separado (botón dorado **RANKED** en el menú principal), inspirado en el antiguo Arena de Fortnite — **siempre contra bots**, sin matchmaking online.

- **Solo** (16 rivales individuales), **Dúos** (8 equipos de 2) o **Tríos** (6 equipos de 3) — el jugador elige, y en Dúos/Tríos sus compañeros son bots por defecto.
- **Dúos/Tríos con amigos reales**: en el menú Ranked, la sección "Jugar con amigos" deja crear una sala (código de 5 letras) para que 2 (Dúos) o 3 (Tríos) personas reales jueguen en el mismo equipo — el resto de los equipos siguen siendo siempre bots, nunca otros jugadores reales (sigue sin haber matchmaking online). El mapa, los equipos rivales y sus posiciones de spawn se generan con una semilla derivada del código de sala, así que todos los que se unen ven exactamente el mismo campo de batalla sin necesidad de transmitirlo. Solo quien crea la sala (el anfitrión) simula la IA de los bots y decide eliminaciones/Top 10/Top 5/Top 3/Victory Royale; el resto de los jugadores reales reciben esas decisiones del anfitrión y las aplican a su propio rango — cada quien gana o pierde puntos Ranked según su propio nivel, igual que si jugara solo.
- Es un battle royale de verdad: todos los equipos están repartidos por el mapa y los bots se disparan entre ellos aunque el jugador no esté cerca. Los equipos van quedando eliminados progresivamente y el juego calcula tu posición final (Top 10 / Top 5 / Top 3 / Victory Royale) en tiempo real.
- **Zona que se cierra (storm)**: un círculo seguro que se va achicando en varias fases a lo largo de la partida — quien queda fuera pierde vida por segundo (cada vez más con cada fase: 2/4/7/11/18 de daño por segundo según qué tan avanzada esté la tormenta), así que esconderse todo el partido ya no es viable pero tampoco te mata de un momento a otro. Hay **130s de gracia total** antes de que la zona empiece siquiera a moverse, y el cierre completo llega recién a los **800s (13.3 min)** — pensado para el mapa mucho más grande (ver abajo), dando tiempo real para explorar, buscar botín y desplazarte entre zonas antes de que el mapa se achique. El HUD y el minimapa muestran el círculo actual **y**, en líneas punteadas, el próximo círculo al que se va a achicar, así que se puede planear la ruta antes de que la zona se mueva. En Ranked con amigos, cada cliente calcula la misma zona de forma determinista a partir del código de sala (igual que el mapa), y cada quien solo aplica el daño de zona a sí mismo y (si es el anfitrión) a los bots que controla — nadie puede dañar al personaje de otro directamente por esta vía.
- **Los bots respetan la zona**: si la tormenta les está haciendo daño de verdad, la prioridad #1 pasa a ser volver adentro — corren en línea recta (con una curva de acercamiento, no en zigzag) hacia el centro de la zona segura, abandonan una pelea activa si están perdiendo mucha vida por la tormenta, y nunca se quedan acampando afuera. Si no hay ningún enemigo cerca, siguen buscando botín o rondan el mapa activamente en vez de quedarse quietos; un detector de "atascado" les fuerza un nuevo rumbo si llevan varias decisiones seguidas sin moverse.
- **Puntos**: +10 por eliminación, +20 al asegurar Top 10, +30 más al asegurar Top 5, +30 más al asegurar Top 3, +50 más si ganas — se van sumando durante la partida, no solo al final.
- **Entry cost**: a partir de Platinum se resta una pequeña cantidad de puntos al iniciar la partida (Platinum -5 hasta Unreal -25).
- **8 rangos** (Bronze a Unreal) calculados en vivo a partir de tus puntos acumulados — subir y bajar de rango es automático según el puntaje, sin nada que "activar".
- **Subdivisiones III → II → I** dentro de Bronze, Silver, Gold, Platinum y Diamond (Elite/Champion/Unreal no tienen — son el tope tal cual): cada uno de esos 5 rangos se reparte en tres tercios iguales de sus mismos puntos de siempre, así que subir de división no cambia el sistema de puntos en nada, solo lo muestra con más detalle ("Diamond II", por ejemplo). Se ve junto al nombre en el Lobby, Profile, el menú Ranked, el leaderboard y la pantalla de resultados, y también como 3 puntitos que se van llenando bajo la insignia misma.
- **La dificultad de los bots depende de tu rango**, no solo en vida/daño: en rangos altos reaccionan más rápido, apuntan mejor, se enganchan a más distancia, huyen/curan con más criterio y usan consumibles con más frecuencia. Además de la escala por rango, todos los bots ahora: buscan cobertura cuando reciben daño reciente (no solo con poca vida), se mueven en curva al acercarse (una inclinación fija por bot, no una línea recta genérica) en vez de acercarse todos igual, alternan entre plantarse a tirotear y moverse en estrafalario según su nivel de puntería, y priorizan la zona segura por encima de seguir peleando cuando la tormenta aprieta (ver arriba).
- Pantalla de resultados con el desglose de puntos y animación de la barra de rango (con aviso especial "RANK UP!" si subes de división), más un leaderboard en el propio menú Ranked (por ahora solo tu fila — preparado para más jugadores si algún día hay multiplayer real).
- **Rango en pantalla**: encima del nombre de cada jugador (el tuyo siempre; el de un rival humano real en online, en cuanto se sincroniza) aparece su rango actual, en el color de ese rango, y se actualiza solo en cuanto suben o bajan de división — no hace falta reabrir nada.
- **Recompensas exclusivas por rango**: la primera vez que alcanzas cada uno de los 8 rangos, desbloqueas para siempre una **skin** (color con gradiente/glow propio) y un **halo** flotante exclusivos de ese rango (ej. Diamond → Diamond Skin + Halo Diamond). Se desbloquean solos (no se compran en la tienda) y aparecen automáticamente en CUSTOMIZE — equipables de forma independiente entre sí y del sombrero, y solo puede haber uno de cada tipo equipado a la vez. Bajar de rango después **no te los quita**.
- **Equipado = equipado, nada más**: el personaje (en el preview de CUSTOMIZE/PROFILE y en partida) siempre refleja exactamente `profile.equippedColor/Hat/Halo` — desbloquear un cosmético nunca lo equipa automáticamente. Un halo equipado se puede volver a pulsar para quitarlo (queda sin halo); todo se guarda al instante con el mismo sistema de perfil de siempre.
- **Identidad visual por rango**: cada rango tiene su propio gradiente/metal/efecto — no un círculo plano con otro color — y todos escalan en exclusividad: Bronze (bronce metálico cálido), Silver (plata pulida gris→blanco→gris), Gold (dorado premium con glow), Platinum (cyan/turquesa futurista, deliberadamente distinto de Silver y Diamond), Diamond (azul hielo/eléctrico con destellos), Elite (violeta→púrpura→magenta con ondas de energía), Champion (rojo/crimson agresivo con puntas de corona), y Unreal — el más impresionante — con un gradiente **holográfico animado** que recorre morado/magenta/rosa/cyan/azul, aura propia y un destello especial periódico. Las tarjetas de CUSTOMIZE usan ese mismo color/gradiente en el borde y el glow (Unreal con borde animado), y el preview de cada una está animado por CSS (sin costo de rendimiento) y crece un poco al pasar el mouse.
- **Insignia propia por rango**: cada uno de los 8 rangos tiene su propio dibujo — no un mismo escudo genérico repintado de otro color. Bronze es un hexágono simple con un remache; Silver, el mismo hexágono con una flecha ascendente; Gold, un escudo con un destello de 4 puntas; Platinum, un diamante facetado con una línea de brillo; Diamond, una gema completa con corona/faceta/pabellón; Elite, una estrella de 8 puntas afilada; Champion, un medallón flanqueado por ramas de laurel; y Unreal, un estallido de estrellas en capas con un núcleo brillante — el diseño se vuelve visiblemente más elaborado a medida que sube el rango, y todo es arte original de Axel's Royale (nada calcado de otro juego). Esta insignia aparece en el menú Ranked, en la pantalla de resultados, encima del nombre en el lobby de pre-partida, en el leaderboard y ahora también en **PROFILE**.

## Progresión en partida: sin loadout inicial, pico, recursos y botín

Solo afecta a **Battle Royale** (Ranked Solo/Dúos/Tríos, local o con amigos) — Práctica, 1v1, 2v2 y el online normal siguen exactamente igual que siempre (arrancan con toda la munición y materiales, sin nada de esto).

- **Arrancás solo con el pico**: nada de armas, munición ni materiales al spawnear — hay que encontrarlo todo explorando el mapa, igual que un battle royale de verdad. Las armas ya elegidas antes de la partida (loadout) quedan vacías (0/0) hasta que se recoge algo del suelo.
- **El pico (clic derecho, mismo botón de siempre) ahora sirve para dos cosas**: demoler cofres/muros (igual que antes) y **cosechar recursos** de tres tipos de nodos repartidos por el mapa — 🌲 árboles (madera), 🪨 rocas (piedra) y 🔩 objetos de metal. Cada golpe suma al contador de ese tipo específico y al total de materiales que ya usa el sistema de construcción de siempre. Un nodo aguanta varios golpes antes de agotarse (y desaparece del todo esa partida — no reaparece, igual que un cofre roto). Los tres tipos están repartidos de forma equilibrada en **todos** los mapas, viejos y nuevos.
- **Botín de armas por el suelo**: 120 puntos de armas por partida (escalado junto con el tamaño del mapa — ver abajo), con las armas más fuertes (Francotirador, Fusil) apareciendo bastante menos seguido que las básicas (Pistola, Subfusil) — hay que explorarlas para encontrarlas. Recoger un arma por primera vez la entrega cargada y con algo de reserva; volver a pasar por el mismo tipo de arma rellena la reserva en vez de duplicarla. A diferencia de los cofres de escudo/botiquín (que sí reaparecen), un arma recogida no vuelve a aparecer — el botín de esa partida es limitado.
- **Nueva fila en el HUD** (🌲/🪨/🔩) junto a la barra de materiales, mostrando cuánto llevás cosechado de cada tipo — solo visible en Battle Royale.
- **Los bots también juegan así**: si un bot no tiene ningún arma, buscar una pasa a ser su prioridad (por encima de pelear o vagar, aunque por debajo de escapar de la tormenta), y cosechan recursos cuando están ociosos y con pocos materiales — con el mismo pico que usa el jugador.

### Tres mapas nuevos

Se suman a los 6 de siempre (elegidos al azar igual que ellos):

- **Lago**: un lago grande en el centro del mapa, rodeado de 8 casitas repartidas por toda la orilla y con muelles asomando hacia el agua desde varios lados.
- **Piscina**: una casa grande de varios ambientes (con divisiones internas) alrededor de una piscina, con muebles de patio como cobertura.
- **Mansión**: una mansión de varias habitaciones + un garaje separado + una zona de piscina/terraza, con jardines como cobertura — la más grande y elaborada de las tres.

Los tres tienen su lago/piscina real (no el charquito al azar que sí sale en los otros 6 mapas), y esa zona de agua queda automáticamente libre de nodos de recursos y armas — nada aparece flotando en el agua.

### Mapas ~3 veces más grandes

Los 9 mapas (los 6 originales + Lago/Piscina/Mansión) son ahora **~3 veces más grandes en área** que antes — no solo más espacio vacío alrededor, sino contenido real repartido en la ground extra:

- Cada uno de los 6 mapas originales mantiene su forma reconocible de siempre y suma dos anillos completos de nuevos puntos de interés llegando hasta el borde del mapa más grande. Laberinto pasó de 4x7 a 7x13 segmentos de muro; Lago pasó de 4 a 8 casas; Piscina y Mansión crecieron en cantidad de habitaciones/edificios y sumaron una segunda construcción más pequeña cada uno.
- **Nuevos biomas de terreno**: manchas de montaña (rocosas, con racimos de piedras) y de bosque (verde denso, con racimos de árboles) — antes solo había parches de tierra/arena y props sueltos.
- **Dos caminos independientes** en vez de uno solo — más de una ruta real para moverte entre zonas.
- **Densidad de contenido sin recortar**: nodos de recursos (70→215), botín de armas (40→120), cofres de escudo/botiquín (10→20 puntos) y cobertura extra escalaron junto con el área del mapa, así que no se siente más vacío pese a ser mucho más grande.
- **Distancias de aparición y de "visión" de los bots** escaladas junto con el mapa — los equipos aparecen mucho más separados entre sí, y los bots detectan botín/recursos a una distancia proporcionalmente igual de lejos que antes, en vez de quedarse "ciegos" en el mapa nuevo.
- El **minimapa** ya representaba el mapa como un porcentaje de su tamaño total, así que muestra correctamente todo el mapa nuevo sin ningún cambio adicional.
- La **tormenta** se ajustó para el nuevo tamaño (ver arriba) — más tiempo de gracia y de cierre total, porque desplazarse de un lado al otro del mapa ahora toma más tiempo real.

### Pico como cosmético

- **19 picos distintos**, cada uno con su propio color de mango/cabeza (y brillo/efecto holográfico animado en los de mayor rareza) — puramente visual, nunca cambia el daño ni la cosecha del pico.
- **6 en la ITEM SHOP** (100 a 900 monedas, Common a Legendary) y **13 exclusivos del Pase de Batalla**, repartidos entre los niveles 4 y 92 de ambas rutas — sin tocar ninguno de los hitos de sombreros/colores/weapon skins que ya existían.
- **Categoría "PICO" propia en el LOCKER**, con el mismo sistema de equipar/desbloquear/guardar que color, sombrero, halo y weapon skin.
- El pico equipado se ve en la mano de tu personaje (y el de cualquier otro jugador/bot) en cuanto está desarmado — distinto según lo que cada quien tenga equipado.

## Progresión: monedas, tienda, perfil

- Ganas **+10 monedas** por cada eliminación (contra bots o en online).
- **LOCKER** (antes Customize): elige color, sombrero y halo de tu personaje entre los que ya desbloqueaste — cada tarjeta muestra claramente si está Equipada, Desbloqueada, Bloqueada (🔒) o Bloqueada-con-motivo (rango o nivel de Pase de Batalla necesarios).
- **ITEM SHOP**: gasta monedas para desbloquear colores/sombreros con precio, con 6 rarezas (Common → Mythic). Los cosméticos nuevos del Pase de Batalla (ver abajo) **no** están aquí a propósito — se consiguen jugando, no comprando.
- **PROFILE**: nombre, insignia y progreso de rango actual (con puntos y cuánto falta para el siguiente), monedas, bajas totales, victorias, partidas jugadas (incluye las partidas Ranked) y cosméticos desbloqueados.

## Cosméticos y Pase de Batalla

**18 sombreros nuevos** en total, cada uno un diseño realmente distinto (no el mismo gorro repintado): Visera, Audífonos, Bucket Hat, Boina y Gorro de Fiesta (comunes), Bandana, Casco de Obra y Bandana Deportiva (uncommon), Sombrero Pirata, Capucha Ninja, Casco Vikingo, Casco Astronauta y Casco Samurái (rare), Sombrero de Mago, Mohawk y Casco Robótico (epic), y Cresta de Dragón y Cresta Fénix (legendary) — más **14 colores nuevos** (Turquesa, Lima, Naranja, Cian Hielo, Gris Carbón, Coral, Índigo, Verde Bosque, Ámbar, Beige Arena, Menta, Magenta, Azul Medianoche, Fucsia). Boina/Gorro de Fiesta/Casco de Obra y Gris Carbón/Coral/Índigo/Verde Bosque/Ámbar están en el **ITEM SHOP**; el resto se consigue jugando, a través del Pase de Batalla.

**WEAPON SKINS** (sección propia en LOCKER, entre Sombrero y Halo): 11 skins que repintan el arma que tengas en mano — **puramente visuales, nunca cambian daño, cadencia, alcance, munición ni nada del balance del arma**. Pizarra, Carmesí, Jade y Oro Pulido están en la tienda; Camuflaje, Tóxico, Fibra de Carbono, Neón, Dragón y Holográfica (con un degradado animado) se consiguen por el Pase. Se equipan igual que color/sombrero/halo — un clic, se reflejan al instante, y volver a la Predeterminada es tan simple como volver a seleccionarla.

**PASE DE BATALLA** (botón propio en la barra superior, con tu nivel actual como subtítulo):

- **XP es una moneda totalmente separada de las monedas** — ganas XP jugando: por cada eliminación, por terminar una partida (más si la ganas), por alcanzar Top 10/5/3 en Ranked (esto pasa sí o sí, tengas Ranked activado o no — el XP del pase no es "tu rango"), por tiempo sobrevivido (un goteo lento), y al reclamar un desafío diario o semanal. Las monedas por eliminación (+10 de siempre) no cambian en nada.
- **100 niveles**, con la misma curva de XP de siempre (empieza fácil, se hace más exigente hacia el final) — llegar a 100 es una meta de largo plazo (~228,000 XP en total), no algo que se complete en un par de días. La rareza de las recompensas escala con el nivel: comunes/uncommon en los primeros niveles, rares a mitad de camino, epics entre el 55 y el 80, y legendarias reservadas para el tramo final (85+) — cada ruta (gratis y Premium) termina el nivel 100 con su propia recompensa legendaria, la de Premium (Cresta de Dragón) pensada como la más vistosa de todo el juego.
- La ruta **gratis** reparte un cosmético cada 10 niveles; la ruta **Premium**, cada 5 (el doble de densa) — el resto de niveles en ambas rutas paga monedas. Barra de progreso, nivel actual, XP actual/necesaria y la ruta completa de 100 niveles siempre visibles en la pantalla del Pase — cada recompensa muestra si está bloqueada (por nivel o por Premium), lista para reclamar, o ya reclamada. **Las recompensas nunca se entregan solas** — hay que apretar RECLAMAR.
- **Pase Premium**: cuesta **750 monedas** (entre un objeto Epic y uno Legendary de la tienda — ni regalado ni imposible), se paga con las mismas monedas de siempre, y desbloquea la columna Premium para todos los niveles — incluidos los que ya hayas alcanzado antes de comprarlo.
- **Comprar niveles con monedas**: si no quieres esperar el XP, el botón "COMPRAR NIVEL" avanza exactamente un nivel a la vez — nunca puedes comprar el nivel 50 sin haber pasado antes por el 49, 48, etc. El precio sube con el nivel (50 + nivel×3), así que comprar todo el pase así sale bastante más caro que subir jugando.
- Todo se guarda (XP, nivel, si compraste Premium, qué reclamaste, cosméticos y skin de arma equipados) igual que el resto del perfil — sobrevive a cerrar y reabrir el juego.

## Desafíos: misiones diarias y semanales

Botón **DESAFÍOS** en el menú principal (con un contador de cuántas misiones ya se pueden reclamar). Son 3 misiones diarias + 3 semanales, elegidas al azar de una lista más grande cada vez que expiran — el reinicio diario ocurre a medianoche y el semanal cada lunes (clave de fecha/semana real, no "7 días desde que abriste el juego por primera vez").

- Cada misión está atada a algo que ya pasa en el juego de verdad: conseguir eliminaciones, infligir daño, sobrevivir tiempo total en partida, jugar partidas, ganar una partida, o terminar en el top 5 de Ranked cierta cantidad de veces. El progreso se acumula solo mientras juegas — no hay nada que activar.
- **La recompensa se reclama a mano**: cuando una misión llega a su objetivo aparece un botón "RECLAMAR", nunca se acreditan las monedas solas.
- Las diarias pagan poco (10–35 monedas), las semanales pagan más pero con moderación (70–180) — pensado para que sea un ingreso extra real sin volver trivial comprar cosméticos caros: ni haciendo todos los desafíos todos los días se llega a un mítico (1200 monedas) en un par de días.

### Guardado persistente

Todo el progreso (rango, puntos Ranked, monedas, colores/sombreros desbloqueados, lo que tengas equipado, estadísticas) se guarda automáticamente en el `localStorage` del navegador cada vez que cambia — después de una partida, una compra, un cambio de cosmético o un cambio de rango. No hay un botón de "guardar": simplemente sigue ahí la próxima vez que abras la página, cierres el navegador o recargues. Esto ya existía en el proyecto desde el sistema de perfil original; lo nuevo en esta actualización es un **`playerId`** (un UUID generado la primera vez que juegas) guardado junto con el resto del perfil — identifica a "este navegador" de forma estable sin depender de la IP (que puede cambiar o compartirse entre varias personas).

Es **por dispositivo/navegador**, no una cuenta en la nube: no hay backend/base de datos en este proyecto (`server.py` es un relay sin estado, ver más abajo), así que no hay dónde más guardarlo. Si borras datos de navegación o cambias de navegador, empiezas de cero — y, en el sentido opuesto, nada impide que alguien con acceso a las DevTools de su propio navegador edite su propio `localStorage` para darse monedas o rango infinitos: sin un servidor que valide esos datos, no hay forma de evitarlo del lado del cliente. Si en el futuro se agrega un backend real, este mismo `playerId` es exactamente la clave que usaría para asociar cada jugador con sus datos guardados en una base de datos (`playerId → coins/ranked/owned/...`), y ahí sí las compras/monedas/puntos Ranked deberían validarse en el servidor en vez de confiar en lo que envía el cliente.

## ⚠️ Limitación importante: esto no es a prueba de trampas

El online (1v1 y 2v2) ya conecta **jugadores reales de verdad** desde dispositivos distintos — eso funciona. Lo que sigue sin existir es un **servidor autoritativo**:

`server.py` es un **relay**: agrupa sockets en una sala (2 o 4, según el tipo elegido) y reenvía sus mensajes en crudo entre sí, sin llevar ningún estado de la partida ni validar nada — cada jugador es la fuente de verdad de su propia vida, escudo, munición y bajas, y le avisa a los demás. Esto es perfectamente jugable entre amigos, pero:

- Un cliente modificado podría mentir sobre cuántas monedas gana o cuántas bajas tiene — nada en el servidor lo contradice.
- No hay reconciliación de desacuerdos: si dos clientes ven algo ligeramente distinto (por ejemplo, quién construyó primero en la misma celda), gana quien llegó primero a cada cliente, sin un árbitro central.
- En **Ranked con amigos**, quien crea la sala es además quien simula los bots y decide eliminaciones/placement — un anfitrión malicioso podría, en teoría, mentirle a sus amigos sobre el resultado de la partida (igual que en el resto del online, nada lo audita). Cada jugador real conserva el control total de sus propios puntos Ranked en su propio navegador, así que un anfitrión tramposo solo podría afectar los resultados de esa partida puntual, nunca robar ni modificar los puntos/monedas ya guardados de otro jugador.

### Qué se necesita para eliminar esta limitación

1. **Servidor autoritativo**: reescribir `server.py` para que mantenga el estado real de cada partida (posiciones, vida, escudo, munición, inventario) y sea la fuente de verdad — los clientes envían *intenciones* (mover, disparar, construir) y el servidor decide qué pasó y qué le manda a cada quien.
2. **Monedas/bajas validadas por servidor**: mover el otorgamiento de monedas (`awardElimination()`, hoy en el cliente) a una confirmación del servidor.
3. **Reconciliación cliente-servidor**: con un servidor autoritativo hace falta interpolación/predicción más cuidadosa de la que tiene el relay actual (que ya interpola posiciones, pero no corrige errores del cliente).

El motor del juego (equipos, fuego amigo, IA multi-objetivo, inventario, consumibles, asignación de spawns) ya está generalizado para N jugadores y es exactamente el mismo código que corre en 2v2 local y en 2v2 online — no habría que tocarlo para la fase de servidor autoritativo, solo la capa de red que hoy confía en cada cliente.

## Cómo funciona el multijugador online (lo que sí existe)

No hay una base de datos ni un servidor que "sepa jugar": `server.py` solo agrupa navegadores en una sala (2 para 1v1, 4 para 2v2, o 2/3 para Ranked Dúos/Tríos con amigos) y reenvía mensajes JSON entre ellos (posición, disparos, construcciones, recolección de objetos, equipo). Cada jugador controla y calcula su propio personaje (vida, escudo, muerte, respawn) y le avisa a los demás cuando los golpea — así que todos ven la misma partida sin necesitar un servidor de juego pesado. Los equipos se asignan por orden de entrada a la sala (alternando), de forma idéntica e independiente en cada cliente, así que nadie necesita coordinarse para saber quién es aliado de quién.

En **Ranked con amigos** el esquema es un poco distinto porque hay bots de por medio: el mapa y la posición inicial de cada equipo (humano o bot) se calculan con un generador de números aleatorios sembrado a partir del código de la sala, así que cada cliente construye exactamente el mismo campo de batalla sin que nadie tenga que transmitirlo. Solo el anfitrión (quien creó la sala) ejecuta la IA de los bots; el resto de los bots existen en el navegador de cada amigo únicamente como una copia que se actualiza con la posición/vida que transmite el anfitrión — igual que un rival humano en el online normal. Cuando un amigo le dispara a un bot, ese golpe viaja al anfitrión (el único que de verdad lleva la cuenta de la vida de ese bot) y el resultado autoritativo vuelve a todos en la siguiente actualización. Las decisiones de la partida (quién quedó eliminado, cuándo se aseguró un Top 10/5/3, cuál fue el placement final) también las toma solo el anfitrión y se las comunica al resto, que las aplican a su propio perfil — así nadie calcula su propio resultado por su cuenta y todos terminan de acuerdo en qué pasó.
