import { Component, OnInit, Input } from '@angular/core';

import { CheckResults } from '../checkresults';
import * as Viewer from './viewer';

@Component({
  selector: 'app-board-view',
  templateUrl: './board-view.component.html',
  styleUrls: ['./board-view.component.css']
})
export class BoardViewComponent implements OnInit {
  @Input() data: CheckResults;

  constructor() { }

  ngOnInit() {
  }

  ngOnChanges() {
    //console.log('ngOnChanges: data=', this.data)
    if (this.data && this.data.qdata && this.data.adata) {
      // when all of data is available
      Viewer.update(this.data.qdata, this.data.adata);
    }
  }
}
