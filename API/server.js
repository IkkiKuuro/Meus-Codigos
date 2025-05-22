import express from 'express'
import pkg from '@prisma/client'
const { PrismaClient } = pkg

const prisma = new PrismaClient()
const app = express()

app.use(express.json())

// Criar usuário
app.post('/usuarios', async (req, res) => {
    try {
        const user = await prisma.User.create({
            data: {
                email: req.body.email,
                name: req.body.name,
                age: req.body.age,
            },
        })
        res.status(201).json(user)
    } catch (error) {
        res.status(400).json({ error: 'Erro ao criar usuário', details: error.message })
    }
})

// Listar usuários
app.get('/usuarios', async (req, res) => {
    try {
        const users = await prisma.User.findMany()
        res.json(users)
    } catch (error) {
        res.status(400).json({ error: 'Erro ao buscar usuários', details: error.message })
    }
})

// Atualizar usuário
app.put('/usuarios/:id', async (req, res) => {
    try {
        const user = await prisma.User.update({
            where: { id: req.params.id }, // id é String
            data: {
                email: req.body.email,
                name: req.body.name,
                age: req.body.age,
            },
        })
        res.status(200).json(user)
    } catch (error) {
        res.status(400).json({ error: 'Erro ao atualizar usuário', details: error.message })
    }
})

// Deletar usuário
app.delete('/usuarios/:id', async (req, res) => {
    try {
        await prisma.User.delete({
            where: { id: req.params.id }, // id é String
        })
        res.status(200).json({ message: 'Usuário deletado com sucesso' })
    } catch (error) {
        res.status(400).json({ error: 'Erro ao deletar usuário', details: error.message })
    }
})

// 👇 Isso aqui inicia o servidor!
app.listen(3000, () => {
    console.log('Servidor rodando em http://localhost:3000')
})
