
window.jQuery.fn.center = () ->
  this.css("position","absolute")
  this.css("top", Math.max(0, (($(window).height() - this.outerHeight()) / 2) + $(window).scrollTop()) + "px")
  this.css("left", Math.max(0, (($(window).width() - this.outerWidth()) / 2) + $(window).scrollLeft()) + "px")
  return this

this.cardSide = "question"

this.oppositeSide = (side) ->
  return "answer" if side is "question"
  "question" if side is "answer"

this.updateCard = () ->
  $("#card-#{this.cardSide}").show()
  $("#card-#{oppositeSide(this.cardSide)}").hide()

this.flipCard = () ->
  console.log("flipping")
  this.cardSide = oppositeSide(this.cardSide)
  updateCard()

$(document).ready ->
  updateCard()


bind_slide_keys = () ->
  $('body').keydown = (event) ->
    # if event.keyCode == 27
    if event.keyCode is 37
      window.location.href = prev_url
    else if event.keyCode is 39
      window.location.href = next_url
