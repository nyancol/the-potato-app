import { getSession } from 'next-auth/react';
import { getServerSession } from "next-auth"
import prisma from '../../../lib/prisma';
import { authOptions } from '../../../pages/api/auth/[...nextauth]'


// POST /api/post
// Required fields in body: title
// Optional fields in body: content
export default async function handle(req, res) {
  const { title, content } = req.body;

  const session = await getServerSession(req, res, authOptions)
  const result = await prisma.post.create({
    data: {
      title: title,
      content: content,
      author: { connect: { email: session?.user?.email } },
    },
  });
  res.json(result);
}