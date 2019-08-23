import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-contest',
  templateUrl: './contest.component.html',
  styleUrls: ['./contest.component.css']
})
export class ContestComponent implements OnInit {
  a_number: number;

  constructor() { }

  ngOnInit() {
  }

  onCleared(c: boolean) {
    //console.log('upload-q onCleared', c)
  }

}
