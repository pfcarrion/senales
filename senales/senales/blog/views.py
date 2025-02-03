from django.shortcuts import render, get_object_or_404, redirect
from .models import Blog
from .forms import ComentarioForm
from .models import BlogPost  # Asegúrate de tener un modelo llamado BlogPost, o ajústalo según tu modelo


def detalle_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    comentarios = blog.comentarios.all()

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.blog = blog
            comentario.autor = request.user  # Suponiendo que el usuario está autenticado
            comentario.save()
            return redirect('detalle_blog', blog_id=blog.id)
    else:
        form = ComentarioForm()

    return render(request, 'blogs/detalle_blog.html', {'blog': blog, 'comentarios': comentarios, 'form': form})

def blog_list(request):
    # Obtén todas las entradas del blog desde la base de datos
    posts = BlogPost.objects.all()
    return render(request, 'blogs/lista_blog.html', {'posts': posts})
