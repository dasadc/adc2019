import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FileCheckerComponent } from './file-checker.component';

describe('FileCheckerComponent', () => {
  let component: FileCheckerComponent;
  let fixture: ComponentFixture<FileCheckerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FileCheckerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FileCheckerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
