import React from "react"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import { MainPage, E404, DowPage } from "./pages/main_page"

export function App() {
  return (
    <BrowserRouter>
       <Routes>
         <Route path="*" element={<E404 />}></Route>
         <Route path="/" element={<MainPage />}></Route>
         <Route path="/dow" element={<DowPage />}></Route>
       </Routes>
    </BrowserRouter>
  )
}