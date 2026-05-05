import { useEffect } from "react";

export function useBodyClass(className) {
  useEffect(() => {
    if(!className) return;
    
    document.body.classList.add(className);

    return () => {
      document.body.classList.remove(className);
    };
  }, [className]);
     
}