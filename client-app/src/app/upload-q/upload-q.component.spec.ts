import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UploadQComponent } from './upload-q.component';

describe('UploadQComponent', () => {
  let component: UploadQComponent;
  let fixture: ComponentFixture<UploadQComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UploadQComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UploadQComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
