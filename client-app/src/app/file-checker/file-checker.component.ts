import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file-checker',
  templateUrl: './file-checker.component.html',
  styleUrls: ['./file-checker.component.css']
})
export class FileCheckerComponent implements OnInit {
  checkResults: string;
  
  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  checkFiles() {
    this.adcService.checkFiles()
      .subscribe((txt: string) => {
	//console.log('file-checker: checkFiles:', txt);
	this.checkResults = txt;
      });
  }

  onCleared(c: boolean) {
    //console.log('onCleared: ', c);
    this.checkResults = undefined;
  }
}
