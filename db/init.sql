DROP DATABASE IF EXISTS DAEAlab08;

CREATE DATABASE DAEAlab08;

USE DAEAlab08;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,  -- Nuevo campo para email
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,  -- Campo para categoría
    created_at DATETIME NOT NULL,
    views INT DEFAULT 0  -- Contador de vistas
);


INSERT INTO news (title, content, category, created_at, views) VALUES 
('La Revolucion del Teletrabajo: Cambios Permanentes en el Mundo Laboral', 
'El teletrabajo se ha convertido en una norma mas que en una excepcion. A medida que mas empresas adoptan este modelo, surgen nuevas dinamicas en la cultura laboral. Muchos trabajadores ahora disfrutan de la flexibilidad de trabajar desde casa, lo que les permite equilibrar mejor su vida personal y profesional. Sin embargo, tambien enfrentan desafios como la soledad y la falta de separacion entre el trabajo y el hogar. La implementacion de politicas de bienestar y la creacion de un ambiente virtual colaborativo son esenciales para garantizar el exito de esta modalidad en el futuro.', 
'Trabajo', 
NOW(), 
0),

('Avances en la Investigacion del Cancer: Nuevas Esperanzas para los Pacientes', 
'Investigadores han logrado avances significativos en el tratamiento del cancer, desarrollando terapias personalizadas que se adaptan a las caracteristicas genéticas de cada paciente. Estos tratamientos innovadores prometen aumentar la tasa de supervivencia y mejorar la calidad de vida de quienes enfrentan esta enfermedad devastadora. Ademas, la inmunoterapia ha demostrado ser un cambio de juego al permitir que el sistema inmunologico del propio cuerpo combata las celulas cancerosas. A medida que se realizan mas estudios, la comunidad medica tiene razones para ser optimista sobre el futuro de la oncologia.', 
'Salud', 
NOW(), 
0),

('El Impacto de la Inteligencia Artificial en la Educacion', 
'La inteligencia artificial esta transformando la educacion al ofrecer herramientas personalizadas que se adaptan a las necesidades individuales de los estudiantes. Desde sistemas de tutoría que utilizan algoritmos avanzados para identificar areas de mejora, hasta plataformas de aprendizaje que analizan el rendimiento en tiempo real, la IA esta cambiando la forma en que ensenamos y aprendemos. A medida que mas instituciones educativas adoptan estas tecnologias, se espera que la educacion se vuelva mas accesible y efectiva, permitiendo a los estudiantes aprender a su propio ritmo y de manera mas eficiente.', 
'Tecnologia', 
NOW(), 
0),

('Viajar Despues de la Pandemia: Tendencias y Destinos Favoritos', 
'La industria del turismo se esta recuperando lentamente tras las restricciones impuestas por la pandemia. Los viajeros buscan ahora experiencias que les permitan disfrutar de la naturaleza y desconectar del estres diario. Los destinos de aventura, como montanas y parques nacionales, estan ganando popularidad, asi como los viajes sostenibles que promueven el respeto por el medio ambiente. Ademas, los turistas estan mas interesados en la historia y la cultura de los lugares que visitan, buscando conexiones mas profundas con las comunidades locales.', 
'Viajes', 
NOW(), 
0),

('Sostenibilidad y Energias Renovables: El Futuro es Verde', 
'La transicion hacia fuentes de energia mas sostenibles se esta acelerando, impulsada por la necesidad urgente de combatir el cambio climatico. Gobiernos y empresas de todo el mundo estan invirtiendo en energias renovables como la solar y la eolica, asi como en tecnologias emergentes como la captura de carbono. Estas iniciativas no solo ayudan a reducir las emisiones de gases de efecto invernadero, sino que tambien crean empleos y promueven un futuro mas limpio y saludable para las proximas generaciones. La colaboracion global es clave para lograr un cambio significativo en esta area.', 
'Medio Ambiente', 
NOW(), 
0),

('El Auge de la Alimentacion Saludable: Tendencias 2024', 
'La alimentacion saludable esta ganando terreno en la sociedad actual, impulsada por un creciente interes en el bienestar y la salud preventiva. Desde dietas basadas en plantas que fomentan la reduccion del consumo de carne, hasta la eliminacion del azucar en muchos productos, los consumidores buscan opciones mas saludables y nutritivas. Ademas, las empresas estan respondiendo a esta demanda al ofrecer una variedad de productos que satisfacen estos nuevos estandares. Se espera que 2024 sea un año clave en la transformacion de la industria alimentaria hacia opciones mas sostenibles y saludables.', 
'Alimentacion', 
NOW(), 
0),

('La Influencia de las Redes Sociales en la Politica', 
'Las redes sociales han cambiado drasticamente la forma en que los politicos se comunican con el publico y como se lleva a cabo la campaña electoral. Plataformas como Twitter y Facebook permiten a los candidatos llegar a una audiencia masiva de forma instantanea, pero tambien plantean desafios como la difusion de desinformacion y el ciberacoso. La politica moderna debe adaptarse a este nuevo entorno digital, y los votantes deben ser criticos con la informacion que consumen. La etica en las redes sociales se ha convertido en un tema central en las discusiones politicas contemporaneas.', 
'Politica', 
NOW(), 
0),

('Cine y Cultura: Las Peliculas Mas Esperadas de 2024', 
'Con una lista impresionante de estrenos, 2024 promete ser un gran año para el cine. Desde secuelas de franquicias iconicas hasta innovaciones en narracion y tecnicas de filmacion, los amantes del cine tienen mucho que esperar. Las producciones estan explorando temas relevantes y provocativos, con un enfoque en la diversidad y la inclusion. La participacion de directores emergentes y la adaptacion de obras literarias a la pantalla grande son tendencias que marcan el camino para el futuro del septimo arte.', 
'Cultura', 
NOW(), 
0),

('Desarrollo Sostenible: Progresos y Retos en la Agenda Global', 
'El desarrollo sostenible se ha convertido en un tema central en las agendas politicas y economicas del mundo. Los paises estan trabajando para alcanzar los Objetivos de Desarrollo Sostenible (ODS) establecidos por la ONU, que buscan erradicar la pobreza, proteger el planeta y asegurar la prosperidad para todos. Sin embargo, muchos retos persisten, como el acceso desigual a recursos y la necesidad de politicas efectivas que promuevan la equidad social. La colaboracion internacional y la voluntad politica son esenciales para avanzar en este ambito.', 
'Sostenibilidad', 
NOW(), 
0),

('El Futuro de la Alimentacion: Innovaciones que Cambian el Juego', 
'A medida que la poblacion mundial sigue creciendo, la forma en que producimos y consumimos alimentos debe evolucionar. Innovaciones como la agricultura vertical, la proteina a base de plantas y la biotecnologia estan cambiando la forma en que vemos la alimentacion. Estas tecnologias no solo buscan aumentar la produccion de alimentos, sino que tambien se enfocan en reducir el impacto ambiental de la agricultura. La seguridad alimentaria es una prioridad global que requiere atencion urgente y soluciones sostenibles.', 
'Alimentacion', 
NOW(), 
0);

INSERT INTO news (title, content, category, created_at) VALUES
('La Revolucion de la Energia Solar', 
'La energia solar se ha convertido en una de las fuentes mas prometedoras de energia renovable. Con avances en tecnologia fotovoltaica, cada vez mas hogares y empresas optan por paneles solares. Este cambio no solo reduce la dependencia de combustibles fosiles, sino que tambien puede resultar en ahorros significativos en las facturas de electricidad a largo plazo.', 
'Energia', 
NOW()),

('Tendencias en Marketing Digital para 2024', 
'El marketing digital esta en constante evolucion. En 2024, las marcas estan cada vez mas enfocadas en la personalizacion y en las experiencias del usuario. Las estrategias que incluyen inteligencia artificial y analisis de datos estan liderando el camino, permitiendo a las empresas adaptar sus mensajes y ofertas a las preferencias individuales de los consumidores.', 
'Marketing', 
NOW()),

('Innovaciones en la Industria Automotriz', 
'La industria automotriz esta experimentando un cambio radical con la llegada de vehiculos electricos y autonomos. Las principales marcas estan invirtiendo fuertemente en investigacion y desarrollo para ofrecer modelos mas eficientes y sostenibles. Estas innovaciones no solo estan transformando el mercado, sino que tambien estan estableciendo nuevos estandares de seguridad.', 
'Automoviles', 
NOW()),

('El Impacto de la IA en la Educacion', 
'La inteligencia artificial esta revolucionando la educacion. Desde plataformas de aprendizaje personalizadas hasta herramientas de analisis de desempeno, la IA esta facilitando un enfoque mas centrado en el estudiante. Esto esta mejorando la retencion del conocimiento y adaptando los metodos de ensenanza a las necesidades individuales.', 
'Educacion', 
NOW()),

('Ciberseguridad: Retos y Soluciones', 
'La ciberseguridad se ha vuelto una preocupacion primordial en el mundo digital. Con el aumento de las violaciones de datos y ataques ciberneticos, las empresas deben adoptar estrategias robustas para proteger su informacion. Desde la educacion del personal hasta la implementacion de tecnologias avanzadas, las soluciones son diversas y criticas.', 
'Tecnologia', 
NOW()),

('Avances en la Medicina Regenerativa', 
'La medicina regenerativa esta cambiando la forma en que se tratan diversas enfermedades. Con el uso de celulas madre y terapias geneticas, los medicos ahora tienen herramientas para reparar tejidos y organos dañados. Estos avances estan ofreciendo esperanzas a muchos pacientes con enfermedades cronicas y degenerativas.', 
'Salud', 
NOW()),

('Crecimiento del E-Commerce en America Latina', 
'El comercio electronico ha experimentado un crecimiento exponencial en America Latina. La pandemia acelero esta tendencia, con mas consumidores optando por compras en linea. Esto ha llevado a las empresas a adaptar sus estrategias y a ofrecer experiencias de compra mas atractivas y convenientes.', 
'Negocios', 
NOW()),

('El Futuro del Trabajo: Tendencias para 2024', 
'El futuro del trabajo esta siendo moldeado por la tecnologia y la cultura laboral. Con el aumento del teletrabajo y la automatizacion, las habilidades blandas son mas importantes que nunca. La adaptabilidad, la comunicacion y la creatividad son cualidades clave que los empleadores buscan en los candidatos de hoy.', 
'Trabajo', 
NOW());
