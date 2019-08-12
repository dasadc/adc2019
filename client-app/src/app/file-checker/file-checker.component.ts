import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
import { CheckResults } from '../checkresults';

@Component({
  selector: 'app-file-checker',
  templateUrl: './file-checker.component.html',
  styleUrls: ['./file-checker.component.css']
})
export class FileCheckerComponent implements OnInit {
  checkResults: string;
  boardData: CheckResults;
  
  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

  checkFiles() {
    this.adcService.checkFiles()
      .subscribe((results: CheckResults) => {
	let txt: string = results.info;
	let qdata: string = results.qdata;
	let adata: string = results.adata;
	this.checkResults = txt;
	this.boardData = results;
      });
  }

  onCleared(c: boolean) {
    this.checkResults = undefined;
  }
}
