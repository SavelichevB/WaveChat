import { Navigate } from "react-router-dom"
import React from "react"
import { useAuth } from "../hooks/useAuth"
import "../components/index.css"

export const loading_block = (
    <>
     <div className="loading-moment">
        <div></div>
     </div>
    </>
)

export function PublicRoute({ children }) {
    const { isAuth, load } = useAuth()

    if(load) {
        return loading_block
    }

    if(isAuth){
      return <Navigate to="/k/" replace />
    }

    return children
}

export function PrivateRoute({ children }){
    const { isAuth, load } = useAuth()
    
    if(load) {
        return loading_block
    }
    
     if(!isAuth){
       return <Navigate to="/" replace />
    }   

    return children
} 