import React, { use, useState } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { Main_chats } from '../components/chat/chat'

export function ChatPage() {
   const { username } = useParams()

     const getCleanUsername = () => {
         if (!username) return null
         return username.replace('@', '').trim()
     }
   
     const cleanUsername = getCleanUsername()

   return (
     <Main_chats initUsername={cleanUsername} />
   )
}