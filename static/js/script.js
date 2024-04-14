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


function addInputs(){
  var newInputName = document.createElement("input");
  newInputName.setAttribute("type", "text");
  newInputName.setAttribute("class", "validate white-text");
  newInputName.setAttribute("name", "workout_name[]");
  newInputName.setAttribute("placeholder", "Workout Name")
  newInputName.setAttribute("minlength", "3");
  newInputName.setAttribute("maxlength", "50");

  var newInputSets = document.createElement("input");
  newInputSets.setAttribute("type", "number");
  newInputSets.setAttribute("class", "validate white-text");
  newInputSets.setAttribute("name", "workout_sets[]");
  newInputSets.setAttribute("placeholder", "Sets");
  newInputSets.setAttribute("required", "");


  var newInputWeight = document.createElement("input");
  newInputWeight.setAttribute("type", "number");
  newInputWeight.setAttribute("class", "validate white-text");
  newInputWeight.setAttribute("name", "workout_weight[]");
  newInputWeight.setAttribute("placeholder", "Weight");
  newInputWeight.setAttribute("required", "");
  newInputWeight.setAttribute("step", "5");

  var newInputReps = document.createElement("input");
  newInputReps.setAttribute("type", "number");
  newInputReps.setAttribute("class", "validate white-text");
  newInputReps.setAttribute("name", "workout_reps[]");
  newInputReps.setAttribute("placeholder", "Reps");
  newInputReps.setAttribute("required", "");

  document.querySelector(".workout-name").appendChild(newInputName)
  document.querySelector(".workout-sets").appendChild(newInputSets)
  document.querySelector(".workout-weight").appendChild(newInputWeight)
  document.querySelector(".workout-reps").appendChild(newInputReps)

  
}


function removeInputs() {
  var parentDivName = document.querySelector(".workout-name");
  var parentDivSets = document.querySelector(".workout-sets");
  var parentDivWeight = document.querySelector(".workout-weight");
  var parentDivReps = document.querySelector(".workout-reps");

  removeChildIfExists(parentDivName);
  removeChildIfExists(parentDivSets);
  removeChildIfExists(parentDivWeight);
  removeChildIfExists(parentDivReps);
}

function removeChildIfExists(parentDiv){
  var inputFields = parentDiv.querySelectorAll("input");

  if (inputFields.length > 1) { 
    parentDiv.removeChild(inputFields[inputFields.length - 1]);
  }
}