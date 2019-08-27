import { Component, OnInit } from '@angular/core';

import { AdcService } from '../adc.service';
//import { QNumberList, ANumberList } from '../apiresponse';

@Component({
  selector: 'app-score',
  templateUrl: './score.component.html',
  styleUrls: ['./score.component.css']
})
export class ScoreComponent implements OnInit {
score: Object;
score_board: Object;
score_board_num: number;
score_board_header: string[];
teams: string[];
ok_point: Object;
q_point: Object;
bonus_point: Object;


  constructor(private adcService: AdcService) { }

  ngOnInit() {
    this.getScore();
  }

  refreshScore() {
    this.getScore();
  }

  createArray(data, teams) {
    let tbl = [];
    let rowLabel = Object.keys(data).sort();
    for (let r=0; r<rowLabel.length; r++) {
      let rowName = rowLabel[r];
      let row = [rowName];
      for (let c=0; c<teams.length; c++) {
        let team = teams[c];
        if (data[rowName][team] === void 0) {
          row.push('0');
        } else {
          row.push(''+data[rowName][team]);
        }
      } // loop c
      tbl.push(row.slice(0));
    } // loop r
    //console.log(tbl);
    return tbl;
  }

  createData() {
    let s = this.score['score_board'];
    let h = s['/header/'];
    let n = h.length;
    this.score_board = s;
    this.score_board_num = n;
    this.score_board_header = h;
    this.teams = Object.keys(this.score_board).slice(1)
    this.ok_point = this.createArray(this.score['ok_point'], this.teams);
    this.q_point = this.createArray(this.score['q_point'], this.teams);
    this.bonus_point = this.createArray(this.score['bonus_point'], this.teams);
  }

  getScore() {
    this.adcService.getScore()
      .subscribe(res => {
        //console.log('score getScore: res=', res);
        this.score = res;
        this.createData();
      });
  }

  viewA(q: string, team: string, i: number, j: number) {
    console.log(q, team, i, j);
  }
}
