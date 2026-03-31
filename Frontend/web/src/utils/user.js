import { apiSend } from "./api"

export const api_users = {
    get_user_me: async () => {
        const res = await apiSend.get('users/me')
        return res
    },
    get_user_id: async (id) => {
        const res = await apiSend.post('users/get', {id})
        return res
    }
}