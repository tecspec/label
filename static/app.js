(function(){
"use strict";

function MainController($http){
	var vm = this;
	vm.model = {
				inputTag: "",
				unitData: null
	};
	vm.setUnitData = setUnitData;
	vm.getUrlSrc = getUrlSrc;
	vm.saveOrder = saveOrder;

		activate();

		//////////

		function activate(){
				$http.get("/get-unit-tag-list")
				.then(getUnitTagList);
		}

		function getUnitTagList(e){
				vm.model.units = e.data;
		}

		function setUnitData() {
				var unitData = _.find(vm.model.units, setCorrectUnitData);
				vm.model.unitData = unitData ? unitData : null;

				function setCorrectUnitData(item) {
						var inputTag = vm.model.inputTag.replace(/ /, '');
						return (item.unit_tag.toLowerCase() === inputTag.toLowerCase()) 		
				}
		}

		function getUrlSrc() {
				if(vm.model.unitData){
						var unitData = vm.model.unitData;
						var unitString = unitData.unit_type.split("-").join("").substr(0,2);
						var unitAppend = unitData["air_l_?"] === "L" ? unitData["air_l_?"] : unitData["air_r_?"];
						return "/img/" + unitString + unitAppend + unitData["pass_through?"] + ".jpg";
				} else {
						return null;
				}
		}

		function saveOrder() {
			$http({
					url:"/save-unit-tag-order" ,
					data: JSON.stringify(vm.model.unitData),
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
			});
		}

		}

		var app = angular.module("PipeApp", []);
		app.controller("MainController", MainController);

})();
