$(document).ready(function(){
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $('select').formSelect();
    $('.tooltipped').tooltip();
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
  
/* This function was taken online and implemented */
  function visibility(event) {
    let element = event.target.parentNode.parentNode;
    let input = element.querySelector("input");
    if (input.type === 'password') {
      input.type = 'text';
      event.target.classList.remove('fa-eye-slash');
      event.target.classList.add('fa-eye');
    } else {
      input.type = 'password';
      event.target.classList.remove('fa-eye');
      event.target.classList.add('fa-eye-slash');
    }
  }