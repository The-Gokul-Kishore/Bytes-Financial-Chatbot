export interface User {
  username: string;
  email: string;
  client_id: number;
}

export interface Thread {
  thread_id: number;
  thread_type: string;
  created_at: string;
}

export interface Chat {
  chat_id: number;
  thread_id: number;
  content: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  email: string;
} 