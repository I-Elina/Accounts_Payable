import { useState, useEffect } from 'react';

export function useReviewer() {
  const [reviewer, setReviewerState] = useState(() => {
    try {
      return localStorage.getItem('reviewer_name') || 'Shree';
    } catch (e) {
      return 'Shree';
    }
  });

  const setReviewer = (name) => {
    setReviewerState(name);
    try {
      localStorage.setItem('reviewer_name', name);
    } catch (e) {
      // Storage error fallback
    }
  };

  return [reviewer, setReviewer];
}
