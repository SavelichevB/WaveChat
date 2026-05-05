import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { api_messages } from "../utils/chat"
import { useAuth } from "./useAuth"

export function useMessage() {

    const [id, setId] = useState(null)
    const [load, setLoad] = useState(true)

    const {id: authId, load: authLoad} = useAuth() || {}
    
    useEffect(() => {
       setId(authId); setLoad(authLoad)
    }, [authId, authLoad])

    const get_message = async (chat_id) => {
        setLoad(true)
        try {
            const res = await api_messages.get_message(chat_id)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error get messages', error)
            return false           
        }
        finally {
            setLoad(false)
        }
    }
    const send_message_chat_id = async (chat_id, text) => {
        setLoad(true)
        try {
            const res = await api_messages.send_chat_message(chat_id, text)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error Send Message, since chat_id', error)
            return false           
        }
        finally {
            setLoad(false)
        }        
    }
    const send_message_user_id = async (from, text) => {
        setLoad(true)
        try {
            const res = await api_messages.send_id_message(from, text)
            if(res?.Success) {
                return { Success: true, status: res._status, data: res.Data }
            }
            return { Success: false, status: res._status }
        }
        catch(error) {
            console.log('Error Send Message, since user_id', error)
            return false           
        }
        finally {
            setLoad(false)
        }        
    }

    return {
        id,
        load,
        get_message,
        send_message_chat_id,
        send_message_user_id
    }
}