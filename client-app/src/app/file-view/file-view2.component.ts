import { Component, OnInit, Input } from '@angular/core';

import { AdcService } from '../adc.service';

@Component({
  selector: 'app-file-view2',
  templateUrl: './file-view2.component.html',
  styleUrls: ['./file-view.component.css']
})
export class FileViewComponent2 implements OnInit {
  @Input() text: string;
  @Input() filename: string;

  constructor(private adcService: AdcService) { }

  ngOnInit() {
  }
}
