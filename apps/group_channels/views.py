from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View
from inertia import render as inertia_render

from apps.parser.models import TelegramChannel
from config.mixins import UserAuthenticationCheckMixin

from apps.group_channels.forms import (
    AddChannelForm,
    CreateGroupForm,
    UpdateGroupForm
)
from apps.group_channels.models import Group


class CreateGroupView(View):
    def post(self, request, *args, **kwargs):
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            if not group.image_url or not group.image_url.strip():
                group.image_url = """
                    data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/
                    2wCEAAkGBxASEg8SEA8PDxIPDw8PDw8PDw8PDw8PFRIWFhURFRUY
                    HSggGBolGxUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGhAQ
                    Fy0dHR0tLS0tLS0tKy0tLS0tLS0tLS0tLS0tLS0tLS0rKy0tLS0tLS0xLS0tKystLSstLSsrN/
                    /AABEIAKgBLAMBIgACEQEDEQH/
                    xAAbAAACAwEBAQAAAAAAAAAAAAACAwABBAUGB/
                    /EADwQAAIBAgMFBQUGBQQDAAAAAAABAgMRBCExBRJBUXFhgZGhsQYTIjLBQlJygrLRIyQzc/
                    BTYqLCY5Lh/8QAGgEAAwEBAQEAAAAAAAAAAAAAAQIDAAQFBv/
                    EACkRAAICAQQBBQABBQEAAAAAAAABAhEhAxIxQXEEIjJRYYEUUpHB8BP/
                    2gAMAwEAAhEDEQA/APIlBMo+zPCKsQsowSimWCwGIU2U2U2YYhTZTYDkYagn
                    IFsFyAcgDUG2BKEXqgXIpyAwpC54ZcG11M1SnKOq70bN4reFcUyikzDvFqY6r
                    QT0yfkZZxaeZJ2iiaY9SCbvkzKpDFIKkZoko2CjItZizcGHvMkWBCQTQwtDi
                    JgQkG0MhRiImDFhsYUai4sXTfmGwijg6bF02EEQchqEoZTMTY+DHwZnixsDEp
                    I1QZdTDU55zhGTta7V8uQEGOiI0RZxmUWyih1FFFspmCU2C2WwGgDIjYDkW0w
                    HFmGRTkA5EcXy8wJQlyAOqKlIByKlCXJip34poRsdINzBcxDmC6gjkOoj98m+
                    Z98m+DeHaaFMk7PJmffCUzbjbRc4NFJjm7oS4iNVwOmHGQxq4hDYSCmBoiGxY
                    E0XTYyFYSHQFzRdNjoVhjYaANBU3n1GFYQ1ZimhlJjCsKLsOEsbF5GJsZTYy
                    IqLGBEY4dFiIjYPIxNmmLHXM9PQfEUjI5LKLYI50EbKI2C2AJbYLZTkA5GGSC
                    bAcgXIXKYB0hjkBKQuVQW6gLGURzmC6gh1QHVA5DqI6dnqkzPUw8Xo93zRPe
                    Fe8EbTHSaMtSnKOunPgBc2b4irS4ojKP0UT+xe8WpAuJBbYw2MhmpnTH0Hmu0e
                    LFaAki4sZViKRnhgWTTJZIWhsF8IplGKjQ1kgEMp/
                    L3i2hmKaHoCg4fKgGMKPkSnqWtF0ACKPkg6YLLp6jCDBqFMZBmEY2A2mJgNg
                    YmzRTYxMVDVDgMjI5TZVyMphOgpsCTLaBcUYZASkKlMY7AOYCiFSm+T8BUnLk/
                    AfKqKlWFY68CJuX3X4CJVHxujU6wDrCNfpReDI6pTqD5qL1S6rIROjyZKSkUV
                    Fe8JvgbjK3RLY1IaphKYgtMykajUoXQqUB+Az3l2XDrUyu242T3U6MI6h80eq
                    AmhuCjecetxIrIzeDRiEZTbiTEyk+RIPBrpr4F3iZGtxtGK7EZZDMETRR+XvY
                    uQ6kvhXiKmN0KuR9L5e8Fh0F8PiDMPQOx1P5QWgqeiKYRRyeSItSQ0REMIOCpgh
                    QMIxkdR0RMdRqRich6NBnNFgMjI5DYDkU5C5NhOpIuUxM6pcl2i5bvXqBlEhc6widV8E/
                    Bj3US5Cp1xH5KpfhnnUfJ+DEyrGl1+0XKqnrYlLyUXgzuqV7wY4x6EVC+hOm
                    PaF75amSVFoBoGUHDNFGSbSfEdUw/YYD0NOG9ThLnFN9SunUrTJaj25OJOmLsd
                    HEUjDUiJONDxlZr2PG85fgfqjViYk2HS+GcubUV3ZsPFF4L2EJP3nLqmrZVPOU
                    uSsurMtTU61GluQS46vqJBXKyk3UaMuJZnowvJLm/IZiJDdn09Zdy+ozzIHER
                    tdmNmmuxVCN5LszYZZYI4RqaskuSM8jRUZntdjMWJpgvhQuQ6SEyCBD6ayXQq
                    QcdF0AkEA6OhSLREERjQoAhwMIw46jkKjwGoxOQ80ozGkUhI4MmJnVKk2x
                    Moriw2d6QNSsZ51W9E/AdKcVwQmdcnJ/paK/BE9/7rFPe5MdKsA6pF19lF4FZl
                    WY6Nbmrm+nhFOO9HNPyfIyhu4ZpT28nJuNoV91p6riuaNFbCtGOcLCuMos
                    Kakju18Gmk1mmrp9hza9Cx6LY8N/DU2+G9DwbsYMdRsdLSkrOWGpUnH6OBOJ6
                    rAUv4FJ8438WzzlWm20lq3ZdT2dWioQhBfYhGPgkiekqkw+pniKOBjI6nKqq7
                    stW9OZ18c9RWyMNvTc38tPznwGmrdDQltjbOhSo+7pxhyWf4nmzm4yZ08XUO
                    NUTlKy1bHlhUJpK8sLZ1DelvPSOnbI2YmY2EFCKS0XmzDiZmS2oa90rM7Tk0
                    lxZ0Ut2KS4IRgqX2nq9Og2tIEVWQydujNWY7Cwsr8/QQo3ZsCvsz4oXUYFCO
                    ZJsbRibs3CCmKis0MmyqSCKOF8RjAgswgHIqOpZIBEY1BwBDiYVhwQ2OqF0x
                    1PUxKQ00iIrNdTQ0KQkeTqVTLUrN6eQ2UVxz9Bc6ttBWz1YpCJxlyA92+PqH
                    Ko2A2yLoqrDhhm9M+hHhHyAjOSd02nzPSbIUcRFqyVSC+JLjH7yGiovBPV1H
                    BX0eZnRaOj7N1bVlTl8tX4ekvsv6d5vxuzrcDkqLhOEuMJwl4STM4bcoG9ak
                    Gj0W0cBa+R53F0bH0bbGFVm+eZ4nadPUo/dE4/Sa25Ha9mKP8onzqVfC9voY
                    dpw1PRbJw+5g8OudPff525fU8/tZ6m0+CelPdqyf6zn7CwnvMRHK8ad6ku75
                    fOx3doz1J7O4XcoyqNZ1nl+CN0vO7Mu0quoYIeUt+r+LBxsXeUlGKu27Jdp1
                    6dJU4KC4avnLizPszD61Zdqh9ZfTxDxdUKXZWTt7V0YcbVLwVDdW89ZeSAo0
                    96V3on4s1zZkryUeFSFV5mKEN59gytK7sOowsDkdYQbyMtWQ6rIRBXYWCKGU
                    IWDmwkKqSNwblgpXZoQulEZJmRmLmxlJC1mx8UFAYMmXTQMhsEYXosKmgJDY
                    IIrCGRASGJGEYyA6itRSRopLLqZkZMZSjmh4vDrXsGMUi3k8LObegO5zGSny
                    AsyVHsobRpQeW8l1yN62W+RzPdM6uwto+6ko1M6UnaV89y/2l9RljlEtXclc
                    TPWwDXAvY1Z0cRSm/l3lGf4JO0v37j2uP2UrXSy4NcUeT2ngrXyDSksHPp+o
                    WqnF9nsNsbP1yPFbTw9mz6XJe8oUp/fo05Pq4q54ramGvUhG3zVIR8ZJCwla
                    OL0Ws7cX0ey2rS+H8q9DwW1KLlJRjrOSjH8Tdl6n0fbUcmeS2ThveYylypuV
                    WX5U7f8ALdBpy9rZL0epti5fR3dqQUIqC0hFRXRKy9DxmJourUhTjrUmo35J
                    6vuV33HrtvVNTj+z2HvOrWekFuQ/FL5n3L9Q0cRH9NLZpubNO0WoJQjlGEVG
                    K7ErI8zWg6k1Bcc5PlHizr7Wr6mTB092Dm/mqZ9IcP38B1hHRo+2N9krySSS
                    ySVkuSOVXe87I2YmpqZqcbZ8Xr2BOnTVKwoRsklwE15jZMySd2ZlYq2SnEe2
                    VCIqvUsDgPLAqSuNpRsKox5mhmQZYwDNiY5sqpO7su8fSgbkNUg0hdSQc5WF
                    U1d3MKl2MpRGyZEhdSV8vEIOWXDNj0gKcQpswr5Kjmx6F00MCKwoobTQCQ6E
                    cjEpMJI02tkKoxu+mY5gIyY+gsurLD3bJLkaMPSTV3zFsg5dnz+lTXGSR1MD
                    gYTyjKMnyTz8DlRpNjY0JLNXTWaayaAvB601fDo70tjtcDBisBbgen9ltoe/
                    TpVf6kVeMv8AUitb9q8zVtTZ2TyNvzTPO/qZQ1Nkh3srV99hIp5yoydGV+SS
                    cX4NLuOTt7B2vkdL2HTjPE0+cYVF1TafqjT7Q4fJk4vbNo5N+z1LS4ef8m3Z
                    Ub4PDf2Yrwy+h52WH3sXh4/+eD7oy3voep2RD+Tw/wDa+rOTs+jvY2m/uKpP
                    /i19RIOt38kdKe2Wo/J0duvJnI9k6HxYmry3aS/VL/qdT2glkxexKW5hYvj
                    UlOo+92XkkZOoV9iwlWh5wcP2gq6j4Ufc4enD7TW/P8Us34ZLuEVaXva9OHD
                    f3pfhjm/S3eO25WzZX6R1dRh/JwK0PeVFHg3eXZFZsLGVM8tF6DcJG0Z1
                    HrJ7sei18/Qw4iZVHdHLr6M0832LzBuFUyy8eotuwTpSFYiYulECTuzRBWF
                    LcIqpNJGON5O5depvOy0Q+hAHLGS2qxkVYTiKvBa8ewLEVd1dr0EUYXzZm+
                    kCK7Y2hTNOiKhGxmr1N52WnHtDwLmTJJ7z7DTSiLo0x8pJIyRpPpA1Z26g0
                    oAQTbuzTCIRXhBAxVypO+Q2EQicIOKCiikHFGJthwjdjioRsuocI3aXMxJs
                    dRjZdfQbQheS7MySNGEhk3zyXQVshKWC5G2EbJLsMtON5JdvkbpISTOab6P
                    M4XZDfA1S2RlocTA4itSacJyX+1u8X2NPI95sbFQxNPeSUZxyqQ5Pg1zTDK
                    TidXqZ6mn7rtHlKdOVCpCrHWnJS6riu9XXefQMVSjOClHNSipJ9jV0cLaeA
                    yeR2dgS3sNTX+nvUn+XTysS1XaUjh9Vqb4xn2sHM2BT3MX+OlUj6P6HR29T
                    +FiaFPdxVF83NeMJHQ21D4WI370yE53qxl+F7Oj/ACtFcqUfQwbFp3xNSX3
                    aTX/tJfsdPBf0ILlSh+ky7Eh/ExD7Ka/UTvEid0p/92YPaR5M24uCp0oQ+5
                    CMfBWM+1Ke9VpR51IX6Xu/IftuXwsp/ah1xCJxNjU7zrVH9mKprq836LxOZ
                    tipdvj+52tnx3aF/vylLzsvQ4qjvVo8k99/lz9bF48tnfpP3uX0Kx63Ixgv
                    sqz68fM5SzfTP9jdtOpeTMNXKF/vPyX+MouDu0l7V+mSTuxWIlZDIGXEyu7
                    GbOyKySjEvFVLKy1YdPJXMU5bz7xG6RRK2MoQNM5qKv8A5cGjGyM1epvPsW
                    hr2o3yYMbyd3xN1GFhOHgMxFXdVlq/IMVWTSd4QOJrfZXf+xVCmKpQN1OOR
                    lnIJPaqQWSM0m5P0LqzvktBlKAROMsOnEOci3kDFBE5yFTiPigYRGWCI2RI
                    dShcCKNW7ZW8TEpMpmjDQyb55ITCF2kuJtmrZLhkBkZvoXa+nE3uNklyE4K
                    neV+EfU0VBGc83mg8FDNvkrd7NDReFhaC7cy2Tbyc7dtnBjszLQdsiTw9eE
                    vsy+Cpy3W1n3a9xCFG7VM6VNzTT7PX47D3TFezisq8OU4zXerf9SEOS/Yzy
                    03/AOckFWhavRf+9ed0bdqx+F9CEB2hO4kwy/hx/tQ/ShWyI/1u2a8l/wDS
                    EA+GCXEjLUjfE0+xzfhFidvv4WQhWPyReHzj4M1eO7RguUI+lziYFZ1Zcoq
                    K73f6EIVjwdej8H5/2cfGO8n1E7SytHkkvAhC56unykZKejfIwrNkIKzrh2
                    MxErRM9GOZCCvkpH4j8TOytzM1KNyyAfyNHETYmoq5kzbIQMgQ+zXRgXXnw
                    XeQg3RNZkDSiaoIhAoWZTzG00QgRJD0rFpEIYiasNTy3n0X7hSIQBK7ZswV
                    KycnxyXTiXUKIKQu5HSw9Ldgub+JgON2lzdiEEOe+zqSjbLkrCWiEERzxZ/
                    /2Q=='
                    """.strip()
            group.owner = request.user
            group.save()
            return inertia_render(request, 'Channels', props={
                "flash": {
                    "success": 'Группа успешно создана'
                },
                "group": {
                    "name": group.name
                }
            }, url='/profile')
        return inertia_render(request, 'Profile', props={
            "form": {
                "name": form.data.get("name", ""),
                "description": form.data.get("description", ""),
                "image_url": form.data.get("image_url", "")
            },
            "errors": form.errors
        })


class UpdateGroupView(View):
    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)
        form = UpdateGroupForm(request.POST, instance=group)

        if form.is_valid():
            form.save()
            return inertia_render(request, 'Profiel', props={
                "flash": {"success": 'Группа успешно изменена'}
            })
        return inertia_render(request, 'Profile', props={
            "form": {
                "name": form.data.get("name"),
                "description": form.data.get("description"),
                "image_url": request.POST.get("image_url", ""),
            },
            "errors": form.errors
        })


class DeleteGroupView(View):
    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)
        group.delete()
        messages.success(request, 'Группа успешно удалена')
        return redirect(reverse('users:profile'))


class GroupDetailView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        group = get_object_or_404(Group, slug=slug)

        channels = group.channels.all()

        auto_category = None
        if hasattr(group, 'auto_rule'):
            auto_category = group.auto_rule.category
            channels = TelegramChannel.objects.filter(category=auto_category)

        is_owner = request.user.is_authenticated and (group.owner == request.user)
        add_form = None
        if is_owner and not hasattr(group, 'auto_rule'):
            free_qs = TelegramChannel.objects.exclude(groups=group)
            add_form = AddChannelForm(channel_qs=free_qs)

        return render(request, 'group_channels/detail.html', {
            'group': group,
            'channels': channels,
            'auto_category': auto_category,
            'add_form': add_form,
            'is_owner': is_owner,
        })


class AddChannelsView(UserAuthenticationCheckMixin, UserPassesTestMixin, View):
    def test_func(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        return self.group.owner == self.request.user

    def post(self, request, slug):
        free_qs = TelegramChannel.objects.exclude(groups=self.group)
        form = AddChannelForm(
            request.POST,
            instance=self.group,
            channel_qs=free_qs
        )

        if form.is_valid():
            self.group.channels.add(*form.cleaned_data['channels'])
            messages.success(request, 'Каналы добавлены')
        else:
            for msg in form.errors.values():
                messages.error(request, msg)

        return redirect('group_channels:group_detail', slug=slug)
