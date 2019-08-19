import { Component, OnInit, Input } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-result-view',
  templateUrl: './result-view.component.html',
  styleUrls: ['./result-view.component.css']
})
export class ResultViewComponent implements OnInit {
  @Input() checkResults: string;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }

}
