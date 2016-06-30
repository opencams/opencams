var app = angular.module('material-website', [
	'jcs-autoValidate',
]);

app.controller('material', function($scope) {

	$scope.formModel = {};

	$scope.onSubmit = function(valid) {
		if (valid) {
			var lida = Ladda.create(document.querySelector("#material-submit-button"));

			lida.start();

			$('#material_form input, #material_form textarea').each(function() {
				$("#submit-form-inputs").append("<input name=\"" + $(this).attr("name") + "\" value=\"" + $(this).val() + "\"/>");
			});

			$("#material-hidden-form-submit").click();
		}
	};
});

$(function() {
	"use strict";

	Waves.attach('.waves-effect');
	Waves.init();
});
