import { apiSend } from "./api"

export const api_chat = {
    get_chat: async () => {
        const res = await apiSend.get('chat/get')
        return res
    },
    get_chat_username: async (username) => {
        const res = await apiSend.post('chat/username', {username})
        return res
    },
    get_chat_info: async (chat_id) => {
        const res = await apiSend.post('chat/info', {chat_id})
        return res
    }
}

export const api_messages = {
    get_message: async (chat_id) => {
        const res = await apiSend.post('message/get', {chat_id})
        return res
    },
    send_chat_message: async (chat_id, text) => {
       const res = await apiSend.post('message/send/chat', {chat_id, text})
       return res
    },
    send_id_message: async (from, text) => {
        const res = await apiSend.post('message/send/id', {from, text})
        return res
    }
}