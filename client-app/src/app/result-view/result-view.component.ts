import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-result-view',
  templateUrl: './result-view.component.html',
  styleUrls: ['./result-view.component.css']
})
export class ResultViewComponent implements OnInit {

  constructor(public adcService: AdcService) { }
  //constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

}
