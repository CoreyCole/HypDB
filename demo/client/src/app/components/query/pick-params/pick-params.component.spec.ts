import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PickParamsComponent } from './pick-params.component';

describe('PickParamsComponent', () => {
  let component: PickParamsComponent;
  let fixture: ComponentFixture<PickParamsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PickParamsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PickParamsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
