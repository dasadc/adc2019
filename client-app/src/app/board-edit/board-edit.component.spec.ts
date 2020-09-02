import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { BoardEditComponent } from './board-edit.component';

import * as d3 from 'd3';

describe('BoardEditComponent', () => {
  let component: BoardEditComponent;
  let fixture: ComponentFixture<BoardEditComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ BoardEditComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(BoardEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
