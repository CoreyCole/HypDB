import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CoarseGrainedComponent } from './coarse-grained.component';

describe('CoarseGrainedComponent', () => {
  let component: CoarseGrainedComponent;
  let fixture: ComponentFixture<CoarseGrainedComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CoarseGrainedComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CoarseGrainedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
