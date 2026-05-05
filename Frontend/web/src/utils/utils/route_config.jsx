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

export const formatTime = (timeStr) => {
    if(!timeStr) return 'None'

    const date = new Date(timeStr)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if(diffMs < 0) return 'Скоро'
    if(diffMins < 2) return 'Только что'
    if(diffDays === 0) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    if(diffDays === 1) return 'Вчера'
    if(diffDays < 7) return `${diffDays} д`

    return date.toLocaleDateString()
}

export const formatTimeChat = (timeStr) => {
    if(!timeStr) return 'None'

    const date = new Date(timeStr)
    const now = new Date()
    
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const nowOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    const diffDays = Math.floor((nowOnly - dateOnly) / 86400000)

    if(diffDays === 0) return 'Сегодня'
    if(diffDays === 1) return 'Вчера'
    if(diffDays === 2) return 'Позавчера'
    
    if(date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString([], { day: 'numeric', month: 'long' })
    }
    
    return date.toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' })
}

export const formatTimeHour = (timeStr) => {
  try {
    if(!timeStr) return 'None'

    const date = new Date(timeStr)

    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  catch(error) {
    console.log('Error format times')
    return '14:05'
  }
}



export const firstNameChat = (chatName) => {
   return chatName?.[0]?.toUpperCase() || '?'
}

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