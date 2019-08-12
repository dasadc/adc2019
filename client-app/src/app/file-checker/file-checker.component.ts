import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file-checker',
  templateUrl: './file-checker.component.html',
  styleUrls: ['./file-checker.component.css']
})
export class FileCheckerComponent implements OnInit {

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  clearQ() {
    this.adcService.clearText1();
  }

  clearA() {
    this.adcService.clearText2();
  }

  checkFiles() {
    this.adcService.checkFiles()
      .subscribe(info => {
	//console.log('file-checker: checkFiles:', info);
      });
  }
}
