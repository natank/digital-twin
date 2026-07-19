import { render } from '@testing-library/react';

import FrontendShared from './frontend-shared';

describe('FrontendShared', () => {
  
  it('should render successfully', () => {
    const { baseElement } = render(<FrontendShared />);
    expect(baseElement).toBeTruthy();
  });
  
});
