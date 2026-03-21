import React from "react"
import { BrowserRouter, Route, Routes } from "react-router-dom"
import { MainPage, E404, DowPage } from "./pages/main_page"
import { RegistePage, LoginPage } from "./pages/auth_page"
import { PrivateRoute, PublicRoute } from "./utils/route_config"

export function App() {
  return (
    <BrowserRouter>
       <Routes>
         <Route path="*" element={<E404 />}></Route>
         <Route path="/" element={<MainPage />}></Route>
         <Route path="/dow" element={<DowPage />}></Route>

         <Route path="/a/reg/:username?" element={
          <PublicRoute>
              <RegistePage />
          </PublicRoute>
         }></Route>

         <Route path="/a/login/:username?" element={
          <PublicRoute>
              <LoginPage />
          </PublicRoute>
          }></Route>

         <Route path="/k/" element={
          <PrivateRoute>
            <h1>This chat...</h1>
          </PrivateRoute>
         }></Route>
       </Routes>
    </BrowserRouter>
  )
}