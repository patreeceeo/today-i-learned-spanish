<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>${card.name} - TIL Spanish flashcards</title>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
    <meta name="keywords" content="python web application" />
    <meta name="description" content="pyramid web application" />
    <link rel="shortcut icon"
          href="${request.static_url('tutorial:static/favicon.ico')}" />
    <link rel="stylesheet"
          href="${request.static_url('tutorial:static/css/application.css')}"
          type="text/css" media="screen" charset="utf-8" />
    <link rel="javascript"
          href="${request.static_url('tutorial:static/js/application.js')}"
          type="text/css" media="screen" charset="utf-8" />
    <!--[if lte IE 6]>
    <link rel="stylesheet"
          href="${request.static_url('tutorial:static/ie6.css')}"
          type="text/css" media="screen" charset="utf-8" />
    <![endif]-->
  </head>
<body>
  <div id="wrap">
    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="brand" href="/">Today I Learned: Spanish!</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              <li class="">
                <a href="/FrontCard">Home</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div id="bottom">
      <div class="bottom">
        <div id="question">
          <p>
            ${card.question}
          </p>
        </div>
        <div id="answer">
          <p>
            ${card.answer}
          </p>
        </div>
        <p>
          <a href="${edit_url}">
            Edit this card
          </a>
        </p>
      </div>
    </div>
  </div>
</body>
</html>
