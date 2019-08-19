import { TestBed } from '@angular/core/testing';

import { AdcService } from './adc.service';

describe('AdcService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: AdcService = TestBed.get(AdcService);
    expect(service).toBeTruthy();
  });
});
