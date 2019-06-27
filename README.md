*Веб-служба, веб-сервис (англ. web service)* — идентифицируемая уникальным веб-адресом (URL-адресом) программная система со стандартизированными интерфейсами, а также HTML-документ сайта, отображаемый браузером пользователя.

Веб-службы могут взаимодействовать друг с другом и со сторонними приложениями посредством сообщений, основанных на определённых протоколах (SOAP, XML-RPC и т. д.) и соглашениях (REST). Веб-служба является единицей модульности при использовании сервис-ориентированной архитектуры приложения.
В обиходе веб-сервисами называют услуги, оказываемые в Интернете. В этом употреблении термин требует уточнения, идёт ли речь о поиске, веб-почте, хранении документов, файлов, закладок и т. п. Такими веб-сервисами можно пользоваться независимо от компьютера, браузера или места доступа в Интернет.

*Django* — свободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC (Model-View-Controller). Проект поддерживается организацией Django Software Foundation.
Сайт на Django строится из одного или нескольких приложений, которые рекомендуется делать отчуждаемыми и подключаемыми. Один из основных принципов фреймворка — DRY (англ. Don't repeat yourself).

Для работы с базой данных Django использует собственный ORM, в котором модель данных описывается классами Python, и по ней генерируется схема базы данных.

Веб-фреймворк Django используется в таких крупных и известных сайтах, как Instagram, Disqus, Mozilla, The Washington Times, Pinterest, YouTube, Google и др.
Также Django используется в качестве веб-компонента в различных проектах, таких как Graphite — система построения графиков и наблюдения, FreeNAS — свободная реализация системы хранения и обмена файлами и др.

Контроллер классической модели MVC примерно соответствует уровню, который в Django называется Представление (англ. View), а презентационная логика Представления реализуется в Django уровнем Шаблонов (англ. Template). Из-за этого уровневую архитектуру Django часто называют «Модель-Шаблон-Представление» (MTV).
Первоначальная разработка Django как средства для работы новостных ресурсов достаточно сильно отразилась на его архитектуре: он предоставляет ряд средств, которые помогают в быстрой разработке веб-сайтов информационного характера. Так, например, разработчику не требуется создавать контроллеры и страницы для административной части сайта, в Django есть встроенное приложение для управления содержимым, которое можно включить в любой сайт, сделанный на Django, и которое может управлять сразу несколькими сайтами на одном сервере. Административное приложение позволяет создавать, изменять и удалять любые объекты наполнения сайта, протоколируя все совершённые действия, и предоставляет интерфейс для управления пользователями и группами (с пообъектным назначением прав).
В дистрибутив Django также включены приложения для системы комментариев, синдикации RSS и Atom, «статических страниц» (которыми можно управлять без необходимости писать контроллеры и представления), перенаправления URL и другое.

Некоторые компоненты фреймворка между собой связаны слабо, поэтому их можно достаточно просто заменять на аналогичные. Например, вместо встроенных шаблонов можно использовать Mako или Jinja.
В то же время заменять ряд компонентов (например, ORM) довольно сложно.
Помимо возможностей, встроенных в ядро фреймворка, существуют пакеты, расширяющие его возможности. Возможности, предоставляемые пакетами, а также полный перечень пакетов удобно отслеживать через специальный ресурс — www.djangopackages.com

Для того чтобы запустить свой джанго-проект, создайте папку, перейдите в нее, создайте Virtual Environment с помощью команды

`python3 -m venv env`

`source env/bin/activate`

Далее устанавливаем django и DRF (*сокр. Django Rest Framework*) с помощью команд

`pip install django`

`pip install djangorestframework`

Чтобы установить проект, нужно прописать

`django-admin startproject <projectName>`В данном случае `projectName` это имя нашей папки

Затем нужно установить проект

`django-admin startapp <appName>` В данном случае `appName` это имя вашего нового приложения

Давайте разберемся со структурой проект Django

**settings.py** - там хранятся все настройки проекта

**urls.py** - там прописываются url для обработчиков

**views.py** - здесь создаются обработчики

**models.py** - здесь создаются модели

**admin.py** - здесь можно настроить, что нужно показывать в админке

Также для нас потребуется создать файл, **serializers.py**, в котором будут находиться сериализаторы для обработчиков

*Сериализация* — процесс перевода какой-либо структуры данных в последовательность битов. Обратной к операции сериализации является операция десериализации (структуризации) — восстановление начального состояния структуры данных из битовой последовательности.

Сериализация используется для передачи объектов по сети и для сохранения их в файлы. Например, нужно создать распределённое приложение, разные части которого должны обмениваться данными со сложной структурой. В таком случае для типов данных, которые предполагается передавать, пишется код, который осуществляет сериализацию и десериализацию. Объект заполняется нужными данными, затем вызывается код сериализации, в результате получается, например, XML-документ. Результат сериализации передаётся принимающей стороне по, скажем, электронной почте или HTTP. Приложение-получатель создаёт объект того же типа и вызывает код десериализации, в результате получая объект с теми же данными, что были в объекте приложения-отправителя.











