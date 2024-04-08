$(document).ready(function(){
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.datepicker').datepicker({
      format: "dd mmmm, yyyy",
      yearRange: [1960,2006],
      defaultDate: "02 07, 1990",
      showClearBtn: true,
      i18n: {
        done: "Select"
      }
      });
    $('.modal').modal();
  });