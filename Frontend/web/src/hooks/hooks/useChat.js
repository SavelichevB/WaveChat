import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { api_chat } from "../utils/chat"
import { useAuth } from "./useAuth"

export function useChat() {

    const [id, setId] = useState(null)
    const [load, setLoad] = useState(true)

    const {id: authId, load: authLoad} = useAuth() || {}
    
    useEffect(() => {
       setId(authId); setLoad(authLoad)
    }, [authId, authLoad])

    const get_chat = async () => {
        setLoad(true)
        try{
            const res = await api_chat.get_chat()
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status}
        }
        catch(error){
            console.log('Error get chats: ', error)
            return false           
        }
        finally{
            setLoad(false)
        }
    }

    const get_chat_username = async (username) => {
        setLoad(true)
        try {
            const res = await api_chat.get_chat_username(username)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error get chat id', error)
            return false           
        }
        finally {
            setLoad(false)
        }
    }

    const get_chat_info = async (chat_id) => {
        setLoad(true)
        try {
            const res = await api_chat.get_chat_info(chat_id)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }            
        }
        catch(error) {
            console.log('Error get chat info', error)
            return false                
        }
        finally {
            setLoad(false)
        }
    }

    return {
        id,
        load,
        get_chat,
        get_chat_username,
        get_chat_info
    }
}